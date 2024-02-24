import socket
import time

import mcl
from cryptography.hazmat.primitives import hashes, hmac
from one_of_n.consts import N, l
from one_of_n.utils import xor_all_elements, xor_bytes
from one_of_two.sender import sender_run_1_of_2_oblivious_transfer
from one_of_two.settings import BUFFER_SIZE, HOST, PORT
from rich import print

messages_X = [mcl.Fr.rnd().serialize() for _ in range(N)]
keys = [(mcl.Fr.rnd(), mcl.Fr.rnd()) for _ in range(l)]

derived_values_Y = []
for index_I, message_I in enumerate(messages_X):
    index_I_in_binary = format(index_I, "b").zfill(l)

    fks_list = []
    for index_j in range(l):
        hmac_fk = hmac.HMAC(
            key=keys[index_j][int(index_I_in_binary[index_j])].serialize(),
            algorithm=hashes.SHA256(),
        )
        hmac_fk.update(index_I.to_bytes())
        fks_list.append(hmac_fk.finalize())

    derived_value = xor_bytes(ba1=message_I, ba2=xor_all_elements(fks_list))
    derived_values_Y.append(derived_value)


# run 1-out-of-2 OT l times with receiver on〈 K_0_j, K_1_j 〉
for key_K_0, key_K_1 in keys:
    sender_session_secret_key = mcl.Fr.rnd()
    sender_run_1_of_2_oblivious_transfer(
        sender_secret_key=sender_session_secret_key,
        m0=key_K_0,
        m1=key_K_1,
    )
    time.sleep(0.1)


# sends all derived messages (Y) to the receiver
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((HOST, PORT))

    for derived_value in derived_values_Y:
        s.sendall(derived_value)
        s.recv(BUFFER_SIZE)
