import typer
from typing_extensions import Annotated
import socket

from .protocol import encode_message

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"

app = typer.Typer()

def encode_commnad(command: str):
    pass

def main(
    server: Annotated[str, typer.Argument()] = DEFAULT_SERVER,
    port: Annotated[int, typer.Argument()] = DEFAULT_PORT,
):
    with socket.socket() as client_socket:
        # connect to server's socket
        client_socket.connect((server, port))

        buffer = bytearray()

        while True:
            command = input(f"{server}:{port}>")

            if command == "quit":
                break
            else:
                encoded_message = encode_message(encode_commnad(command))
                # TODO: send the serialised message to the server here

                while True:
                    pass
                    # TODO: receive the response from the server, deserialise
                    # and display it here


if __name__ == "__main__":
    typer.run(main)
