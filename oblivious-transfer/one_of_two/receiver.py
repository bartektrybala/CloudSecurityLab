import pickle
import secrets
import socket
from typing import Literal, cast

import mcl
from rich import print

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


def get_senders_public_key(conn: socket.socket) -> mcl.G1():
    sender_public_key = mcl.G1()
    sender_public_key.deserialize(conn.recv(BUFFER_SIZE))
    return sender_public_key


def calc_b(
    sender_public_key: mcl.G1, receiver_secret_key: mcl.Fr, c_choice: Literal[0, 1]
) -> mcl.G1:
    if c_choice == 0:
        return public_g * receiver_secret_key
    elif c_choice == 1:
        return sender_public_key + (public_g * receiver_secret_key)


def send_back_calculated_b(conn: socket.socket, calculated_b: mcl.G1) -> None:
    conn.sendall(calculated_b.serialize())


def send_finish_response(conn: socket.socket) -> None:
    conn.sendall(FINISH_PROTOCOL_PREFIX)


def get_ek0_and_ek1(conn: socket.socket) -> Ek0AndEk1:
    return cast(Ek0AndEk1, pickle.loads(conn.recv(BUFFER_SIZE)))


def extract_mc_from_ek(
    ek0_and_ek1: Ek0AndEk1,
    c_choice: Literal[0, 1],
    receiver_secret_key: mcl.Fr,
    sender_public_key: mcl.G1,
) -> mcl.Fr:
    kr = mcl.Fr.setHashOf((sender_public_key * receiver_secret_key).serialize())
    return ek0_and_ek1.ek0 - kr if c_choice == 0 else ek0_and_ek1.ek1 - kr


def receiver_run_1_of_2_oblivious_transfer(
    c_choice: Literal[0, 1],
    receiver_secret_key: mcl.Fr,
) -> mcl.Fr:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                prefix = conn.recv(PREFIX_FIXED_SIZE)
                if prefix == PUBLIC_KEY_PREFIX:
                    sender_public_key = get_senders_public_key(conn=conn)
                    calculated_b = calc_b(
                        sender_public_key=sender_public_key,
                        receiver_secret_key=receiver_secret_key,
                        c_choice=c_choice,
                    )
                    send_back_calculated_b(conn=conn, calculated_b=calculated_b)
                elif prefix == EK0_AND_EK1_PREFIX:
                    ek0_and_ek1 = get_ek0_and_ek1(conn=conn)
                    mc = extract_mc_from_ek(
                        ek0_and_ek1=ek0_and_ek1,
                        c_choice=c_choice,
                        receiver_secret_key=receiver_secret_key,
                        sender_public_key=sender_public_key,
                    )
                    send_finish_response(conn=conn)
                    # print("Receiver finished protocol")
                    break
    return mc


if __name__ == "__main__":
    c_choice = secrets.choice([0, 1])
    print(f"c_choice: {c_choice}")
    receiver_secret_key = mcl.Fr.rnd()

    mc = receiver_run_1_of_2_oblivious_transfer(
        c_choice=c_choice,
        receiver_secret_key=receiver_secret_key,
    )
    print(f"mc: {mc}")
