import pytest
from tinyredis.protocol import *


# "$-1\r\n"
# "*1\r\n$4\r\nping\r\n”
# "*2\r\n$4\r\necho\r\n$5\r\nhello world\r\n”
# "*2\r\n$3\r\nget\r\n$3\r\nkey\r\n”


@pytest.mark.parametrize("buffer, expected", [
    (b"+Par", (None, 0)),
    (b"+Ok\r\n", (SimpleString("Ok"), 5)),
    (b"+Ok\r\n+Go\r\n", (SimpleString("Ok"), 5)),
    (b"-Error message\r\n", (SimpleError("Error message"), 16)),
    (b":0\r\n", (Integer(0), 4)),
    (b":1000\r\n", (Integer(1000), 7)),
    (b"$0\r\n\r\n", (BulkString(b""), 6)),
    (b"$5\r\nhello\r\n", (BulkString(b"hello"), 11)),
    (b"*3\r\n:1\r\n:2\r\n:3\r\n", (Array([Integer(1),Integer(2), Integer(3)]), 16)),
    (b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n", (Array([BulkString(b"hello"), BulkString(b"world")]), 26)),
    (b"*0\r\n", (Array([]), 4))
])


def test_read_frame_simple_string_extra_data(buffer, expected):
    actual = extract_frame_from_buffer(buffer)
    assert actual == expected
