import pickle
import socket

import mcl
from one_of_two.consts import public_g
from one_of_two.my_types import Ek0AndEk1
from one_of_two.settings import (
    BUFFER_SIZE,
    EK0_AND_EK1_PREFIX,
    FINISH_PROTOCOL_PREFIX,
    HOST,
    PORT,
    PREFIX_FIXED_SIZE,
    PUBLIC_KEY_PREFIX,
)
from rich import print


def send_public_key_and_wait_for_calculated_b(public_key: mcl.G1) -> mcl.G1:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))
        s.sendall(PUBLIC_KEY_PREFIX + public_key.serialize())

        serialized_b = s.recv(BUFFER_SIZE)
        received_b = mcl.G1()
        received_b.deserialize(serialized_b)
        return received_b


def send_k0_and_k1_to_receiver_and_wait_for_response(
    b: mcl.G1,
    sender_secret_key: mcl.Fr,
    sender_public_key: mcl.G1,
    m0: mcl.Fr,
    m1: mcl.Fr,
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))

        ek0_and_ek1 = Ek0AndEk1(
            ek0=m0 + mcl.Fr.setHashOf((b * sender_secret_key).serialize()),
            ek1=m1
            + mcl.Fr.setHashOf(
                ((b - sender_public_key) * sender_secret_key).serialize()
            ),
        )
        s.sendall(EK0_AND_EK1_PREFIX + pickle.dumps(ek0_and_ek1))

        finish_response = s.recv(PREFIX_FIXED_SIZE)
        if finish_response == FINISH_PROTOCOL_PREFIX:
            s.close()
            # print("Sender finished protocol")
        else:
            raise ValueError("Sender did not finish protocol")


def sender_run_1_of_2_oblivious_transfer(
    sender_secret_key: mcl.Fr,
    m0: mcl.Fr,
    m1: mcl.Fr,
):
    received_b = send_public_key_and_wait_for_calculated_b(
        public_key=public_g * sender_secret_key
    )
    send_k0_and_k1_to_receiver_and_wait_for_response(
        b=received_b,
        sender_secret_key=sender_secret_key,
        sender_public_key=public_g * sender_secret_key,
        m0=m0,
        m1=m1,
    )


if __name__ == "__main__":
    m0 = mcl.Fr.rnd()
    m1 = mcl.Fr.rnd()

    sender_secret_key = mcl.Fr.rnd()
    sender_public_key = public_g * sender_secret_key

    print(f"m0: {m0}")
    print(f"m1: {m1}")

    sender_run_1_of_2_oblivious_transfer(
        sender_secret_key=sender_secret_key,
        m0=m0,
        m1=m1,
    )
