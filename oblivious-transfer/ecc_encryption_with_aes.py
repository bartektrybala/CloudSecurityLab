import os
from hashlib import sha256

import mcl
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from rich import print

generator = mcl.G1.hashAndMapTo(b"abc")


class Person:
    secret_key: mcl.Fr
    public_key: mcl.G1

    def __init__(self):
        self.secret_key = mcl.Fr.rnd()
        self.public_key = generator * self.secret_key


sender = Person()
receiver = Person()


# ECDH (Elliptic Curve Diffie–Hellman) key exchange SCHEME
# 1. sender --- public_key ---> receiver
# 2. sender <--- public_key --- receiver

receiver_shared_key = sender.public_key * receiver.secret_key
sender_shared_key = receiver.public_key * sender.secret_key

assert receiver_shared_key == sender_shared_key, "a * (b * G) != b * (a * G)"
shared_ecc_key = receiver_shared_key = sender_shared_key
print("ECDH shared key:", shared_ecc_key)


def ecc_point_to_256_bit_key(point: mcl.G1) -> bytes:
    return mcl.Fr.setHashOf(point.serialize()).serialize()


MESSAGE_TO_SEND = b"Super secret message to encrypt with ecc shared key and AES"
padder = padding.PKCS7(128).padder()
padded_data = padder.update(MESSAGE_TO_SEND) + padder.finalize()

key = ecc_point_to_256_bit_key(shared_ecc_key)
cipher = Cipher(
    algorithm=algorithms.AES(key=key),
    mode=modes.CBC(initialization_vector=sha256(key).digest()[:16]),
)

encryptor = cipher.encryptor()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()
print("Encrypted message:", ciphertext)

decryptor = cipher.decryptor()
padded_decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
decrypted_message = unpadder.update(padded_decrypted_message) + unpadder.finalize()
print("Decrypted message:", decrypted_message)
