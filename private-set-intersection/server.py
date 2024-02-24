import pickle
import socket
from typing import cast

import mcl
from my_types import ClientAndServerBlindedSets
from rich import print
from settings import (
    BUFFER_SIZE,
    CLIENTS_SET_PREFIX,
    ENCRYPTED_SETS_PREFIX,
    HOST,
    PORT,
    PREFIX_FIXED_SIZE,
)
from utils import encrypt_set, hash_set_to_fr, hash_set_to_g1, secure_shuffled


def receive_client_set(conn: socket.socket) -> list[mcl.G1]:
    return cast(list[mcl.G1], pickle.loads(conn.recv(BUFFER_SIZE)))


def send_back_encrypted_sets(
    client_set: list[mcl.G1], server_set: list[mcl.Fr], conn: socket.socket
) -> None:
    data = ClientAndServerBlindedSets(client_set=client_set, server_set=server_set)
    conn.sendall(ENCRYPTED_SETS_PREFIX + pickle.dumps(data))


def server_run_psi_protocol(server_private_set: list[bytes], session_key: mcl.Fr):
    shuffled_private_set = secure_shuffled(server_private_set)
    hashed_server_private_set = hash_set_to_g1(shuffled_private_set)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        conn, addr = s.accept()
        with conn:
            prefix = conn.recv(PREFIX_FIXED_SIZE)
            if prefix == CLIENTS_SET_PREFIX:
                client_derived_private_set = receive_client_set(conn=conn)
                encrypted_client_set = encrypt_set(
                    set_to_encrypt=client_derived_private_set,
                    key=session_key,
                )

                server_derived_private_set = encrypt_set(
                    set_to_encrypt=hashed_server_private_set, key=session_key
                )

                send_back_encrypted_sets(
                    client_set=secure_shuffled(encrypted_client_set),
                    server_set=hash_set_to_fr(server_derived_private_set),
                    conn=conn,
                )
                print("Server finished")


if __name__ == "__main__":
    server_private_set = [
        b"apple",
        b"banana",
        b"cherry",
        b"honeydew",
        b"imbe",
        b"jackfruit",
        b"kiwi",
        b"grape",
    ]
    server_session_key = mcl.Fr.rnd()
    server_run_psi_protocol(
        server_private_set=server_private_set, session_key=server_session_key
    )
