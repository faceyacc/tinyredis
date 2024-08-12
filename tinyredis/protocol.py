from dataclasses import dataclass

MESSAGE_SEPARATOR = b"\r\n"

@dataclass
class BulkString:
    data: bytes | None

@dataclass
class SimpleString:
    data: str

@dataclass
class Integer:
    data: int

@dataclass
class SimpleError:
    data: str

@dataclass
class Array:
    data: list[Integer|SimpleString|BulkString] | None

def extract_frame_from_buffer(buffer: bytes):

    if MESSAGE_SEPARATOR not in buffer:
        return None, 0

    match chr(buffer[0]):
        case '+': # Simple Strings
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return SimpleString(buffer[1:sep].decode()), sep + 2
        case '-': # Errors
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return SimpleError(buffer[1:sep].decode()), sep + 2
        case ':': # Integers
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return Integer(int(buffer[1:sep])), sep + 2
        case '$': # Bulk strings
            sep = buffer.find(MESSAGE_SEPARATOR)
            array_length = int(buffer[1:sep])
            data = buffer[sep + 2:sep + 2 + array_length]

            if array_length == -1: # Null Bulk String
                return BulkString(None), sep + 2

            if len(data) == array_length:
                return BulkString(data), sep + 2 + array_length + 2

        case '*': # Arrays
            arr = []

            sep = buffer.find(MESSAGE_SEPARATOR)
            array_length = int(buffer[1:sep])

            # Null Array
            if array_length == -1:
                return Array(None), sep + 2

            for _ in range(array_length):
                frame, offset = extract_frame_from_buffer(buffer[sep + 2:])
                arr.append(frame)
                sep += offset

            # Return None if any element in the array is None
            if None in arr:
                return None, 0

            return Array(arr), sep + 2



    return None, 0
