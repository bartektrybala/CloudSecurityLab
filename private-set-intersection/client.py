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
from utils import decrypt_set, encrypt_set, hash_set_to_fr, hash_set_to_g1


def send_dervied_set_to_server_and_wait_for_response(
    derived_client_private_set: list[mcl.G1],
) -> ClientAndServerBlindedSets:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))
        s.sendall(CLIENTS_SET_PREFIX + pickle.dumps(derived_client_private_set))

        prefix = s.recv(PREFIX_FIXED_SIZE)
        if prefix == ENCRYPTED_SETS_PREFIX:
            return cast(ClientAndServerBlindedSets, pickle.loads(s.recv(BUFFER_SIZE)))
        else:
            raise ValueError("Invalid prefix received from server")


def client_run_psi_protocol(private_set: set[bytes], session_key: mcl.Fr):
    encrypted_sets = send_dervied_set_to_server_and_wait_for_response(
        derived_client_private_set=encrypt_set(
            set_to_encrypt=hash_set_to_g1(private_set),
            key=session_key,
        )
    )
    twice_encrypted_client_set = encrypted_sets.client_set

    # decrypt client's layer of encryption
    encrypted_by_server = decrypt_set(
        set_to_decrypt=twice_encrypted_client_set, key=session_key
    )
    intersection = [
        element
        for element in hash_set_to_fr(encrypted_by_server)
        if element in encrypted_sets.server_set
    ]
    print(f"Intersection cardinality: {len(intersection)}")


if __name__ == "__main__":
    client_private_set = [
        b"apple",
        b"banana",
        b"cherry",
        b"elderberry",
        b"fig",
        b"grape",
        b"lime",
        b"mango",
    ]

    client_session_key = mcl.Fr.rnd()
    client_run_psi_protocol(
        private_set=client_private_set,
        session_key=client_session_key,
    )
