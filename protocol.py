import json

DELIMITER = b"\n"


def encode(message: dict) -> bytes:
    return json.dumps(message).encode("utf-8") + DELIMITER


def send_message(sock, message: dict) -> None:
    sock.sendall(encode(message))


def recv_message(sock, buffer: bytearray) -> dict | None:
    while DELIMITER not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    line, _, rest = buffer.partition(DELIMITER)
    buffer[:] = rest
    return json.loads(line.decode("utf-8"))
