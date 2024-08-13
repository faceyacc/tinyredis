from dataclasses import dataclass

_MSG_SEPARATOR = b"\r\n"
_MESSAGE_SEPARATOR_SIZE = len(b"\r\n")

@dataclass
class BulkString:
    data: bytes

@dataclass
class SimpleString:
    data: str

@dataclass
class Integer:
    data: int

@dataclass
class Error:
    data: str

@dataclass
class Array:
    data: list

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)


def extract_frame_from_buffer(buffer: bytes):
    separator = buffer.find(_MSG_SEPARATOR)

    if separator == -1:
        return None, 0
    else:
        payload = buffer[1:separator].decode()

    match chr(buffer[0]):
        case '+': # Simple Strings
            return SimpleString(payload), separator + _MESSAGE_SEPARATOR_SIZE

        case '-': # Errors
            return Error(payload), separator + _MESSAGE_SEPARATOR_SIZE

        case ':': # Integers

            return Integer(int(payload)), separator + _MESSAGE_SEPARATOR_SIZE

        case '$': # Bulk strings
            array_length = int(payload)

            data = buffer[separator + _MESSAGE_SEPARATOR_SIZE:separator + _MESSAGE_SEPARATOR_SIZE + array_length]

            if array_length == -1: # Null Bulk String
                return BulkString(None), separator + _MESSAGE_SEPARATOR_SIZE

            if len(data) == array_length:
                return BulkString(data), separator + _MESSAGE_SEPARATOR_SIZE + array_length + _MESSAGE_SEPARATOR_SIZE

        case '*': # Arrays
            arr = []

            array_length = int(payload)

            # Null Array
            if array_length == -1:
                return Array(None), separator + _MESSAGE_SEPARATOR_SIZE # type: ignore

            for _ in range(array_length):
                frame, offset = extract_frame_from_buffer(buffer[separator + _MESSAGE_SEPARATOR_SIZE:])
                arr.append(frame)
                separator += offset

            # Return None if any element in the array is None
            if None in arr:
                return None, 0

            return Array(arr), separator + _MESSAGE_SEPARATOR_SIZE

    return None, 0



def encode_message(message):
    if isinstance(message, SimpleString):
        return f"+{message.data}\r\n".encode()

    if isinstance(message, Error):
        return f"-{message.data}\r\n".encode()

    if isinstance(message, Integer):
        return f":{message.data}\r\n".encode()

    if isinstance(message, BulkString):
        if message.data is None:
            return b"$-1\r\n"
        return f"${len(message.data)}\r\n{message.data}\r\n".encode()

    if isinstance(message, Array):
        if message.data is None:
            return b"*-1\r\n"
        return f"*{len(message.data)}\r\n".encode() + b"".join([encode_message(m) for m in message.data]) # type: ignore

    return None
