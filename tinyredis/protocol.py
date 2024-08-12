from dataclasses import dataclass

MESSAGE_SEPARATOR = b"\r\n"

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
class SimpleError:
    data: str

@dataclass
class Array:
    data: list[Integer|SimpleString|BulkString]

def extract_frame_from_buffer(buffer: bytes):
    match chr(buffer[0]):
        case '+':
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return SimpleString(buffer[1:sep].decode()), sep + 2
        case '-':
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return SimpleError(buffer[1:sep].decode()), sep + 2
        case ':':
            sep = buffer.find(MESSAGE_SEPARATOR)
            if sep != -1:
                return Integer(int(buffer[1:sep])), sep + 2
        case '$':
            sep = buffer.find(MESSAGE_SEPARATOR)
            length = int(buffer[1:sep])
            data = buffer[sep + 2:sep + 2 + length]
            if len(data) == length:
                return BulkString(data), sep + 2 + length + 2

        case '*':
            arr = []
            sep = buffer.find(MESSAGE_SEPARATOR)
            array_length = int(buffer[1:sep])

            for _ in range(array_length):
                frame, offset = extract_frame_from_buffer(buffer[sep + 2:])
                arr.append(frame)
                sep += offset

            return Array(arr), sep + 2



    return None, 0
