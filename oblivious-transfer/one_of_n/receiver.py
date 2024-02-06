import secrets
import socket

import mcl
from cryptography.hazmat.primitives import hashes, hmac
from rich import print

from one_of_n.consts import N, l
from one_of_n.utils import xor_all_elements, xor_bytes
from one_of_two.receiver import receiver_run_1_of_2_oblivious_transfer
from one_of_two.settings import BUFFER_SIZE, HOST, PORT

receiver_secret_keys = [mcl.Fr.rnd() for _ in range(l)]

choice = secrets.choice([i for i in range(N)])
choice_in_binary = format(choice, "b").zfill(3)
print(f"choice: {choice}, {choice_in_binary}")

extracted_sender_keys = []
for index_j, receiver_secret_key in enumerate(receiver_secret_keys):
    key = receiver_run_1_of_2_oblivious_transfer(
        c_choice=int(choice_in_binary[index_j]),
        receiver_secret_key=receiver_secret_key,
    )
    extracted_sender_keys.append(key)

print(f"extracted_sender_keys: {extracted_sender_keys}")

# get derived values from sender
derived_values_Y = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    s.listen()
    conn, addr = s.accept()

    with conn:
        for _ in range(N):
            derived_values_Y.append(conn.recv(BUFFER_SIZE))
            conn.sendall(b"ack")

fks_reverse_list = []
for sender_key in extracted_sender_keys:
    hmac_fk = hmac.HMAC(key=sender_key.serialize(), algorithm=hashes.SHA256())
    hmac_fk.update(choice.to_bytes())
    fks_reverse_list.append(hmac_fk.finalize())

message = xor_bytes(
    ba1=derived_values_Y[choice],
    ba2=xor_all_elements(fks_reverse_list),
)
print(f"message: {message}")
