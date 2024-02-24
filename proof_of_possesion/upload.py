import pickle
import socket
import struct
from typing import cast

from mcl.structures.G1 import G1
from my_types import ServerChallenge, TaggedBlock
from rich import print
from settings import CHALLANGE_PREFIX, FILE_PREFIX, HOST, PAGE_SIZE, PORT


def send_block_file(
    tagged_blocks: list[TaggedBlock], block_index: int, block_id: str
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(FILE_PREFIX + pickle.dumps((block_index, tagged_blocks)))
        print(f"Block index: {block_index} id: {block_id} sent")


def send_challange_and_wait_for_response(challange_for_server: ServerChallenge) -> G1:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # we need to send a length of the challange message to avoid deadlock
        # between client and server
        challenge_bytes = pickle.dumps(challange_for_server)
        challenge = struct.pack("!I", len(challenge_bytes)) + challenge_bytes

        s.sendall(CHALLANGE_PREFIX + challenge)
        data = s.recv(PAGE_SIZE)
        return cast(G1, pickle.loads(data))
