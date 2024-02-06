import pickle
import socket
import struct
from hashlib import sha256
from pathlib import Path
from typing import cast

from rich import print

from challenge import agg_gen_proof
from my_types import ServerChallenge, TaggedBlock
from settings import (
    CHALLANGE_PREFIX,
    FILE_PREFIX,
    HOST,
    PAGE_SIZE,
    PORT,
    PREFIX_FIXED_SIZE,
)


def receive_data(conn: socket.socket) -> bytes:
    full_data = b""
    while True:
        data = conn.recv(PAGE_SIZE)
        if not data:
            break
        full_data += data
    return full_data


def recv_fixed_length_data(conn: socket.socket, length: int) -> bytes:
    data = b""
    while length > 0:
        data += conn.recv(PAGE_SIZE if length > PAGE_SIZE else length)
        length -= PAGE_SIZE
    return data


def persist_block(
    tagged_blocks: list[TaggedBlock], block_id: str, block_index: int
) -> None:
    block_path = Path(f"server_file/{block_index}/{block_id}")
    block_path.parent.mkdir(parents=True, exist_ok=True)

    with open(block_path, mode="wb") as file:
        file.write(pickle.dumps(tagged_blocks))
    print(f"Block {block_index}/{block_id} persisted")


def handle_file_block(conn: socket.socket) -> None:
    tagged_block_data = receive_data(conn=conn)
    block_index, tagged_blocks = cast(
        tuple[int, list[TaggedBlock]], pickle.loads(tagged_block_data)
    )

    raw_file_data = b"".join([tagged_block.m for tagged_block in tagged_blocks])
    block_id = sha256(raw_file_data).hexdigest()
    persist_block(
        tagged_blocks=tagged_blocks, block_id=block_id, block_index=block_index
    )


def send_back_the_proof(conn: socket.socket, p: bytes) -> None:
    conn.sendall(p)


def handle_challange(conn: socket.socket) -> None:
    challenge_msg_length = struct.unpack("!I", conn.recv(4))[0]
    challenge_bytes = recv_fixed_length_data(conn=conn, length=challenge_msg_length)

    server_challenge = cast(ServerChallenge, pickle.loads(challenge_bytes))
    print(
        f"Challange received g_r: {server_challenge.g_r} x_c: {server_challenge.x_c} g_r_poly0: {server_challenge.g_r_poly0}"
    )

    p = agg_gen_proof(server_challenge=server_challenge)
    send_back_the_proof(conn, pickle.dumps(p))
    print(f"Proof: {p}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(PREFIX_FIXED_SIZE)
            if data.startswith(FILE_PREFIX):
                handle_file_block(conn)
            elif data.startswith(CHALLANGE_PREFIX):
                handle_challange(conn)
