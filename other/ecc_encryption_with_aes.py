import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Person:
    secret_key: ec.EllipticCurvePrivateKey
    public_key: ec.EllipticCurvePublicKey

    def __init__(self):
        self.secret_key = ec.generate_private_key(curve=ec.BrainpoolP256R1())
        self.public_key = self.secret_key.public_key()


client = Person()
server = Person()


# ECDH (Elliptic Curve Diffie–Hellman) key exchange SCHEME
# 1. client --- public_key ---> server
# 2. client <--- public_key --- server

client_shared_key = server.secret_key.exchange(ec.ECDH(), client.public_key)
server_shared_key = client.secret_key.exchange(ec.ECDH(), server.public_key)
assert client_shared_key == server_shared_key


MESSAGE_TO_SEND = b"Super secret message to encrypt with ecc shared key and AES"
padder = padding.PKCS7(128).padder()
padded_data = padder.update(MESSAGE_TO_SEND) + padder.finalize()


## CLIENT ENCRYPTS MESSAGE WITH SHARED KEY ##
iv = os.urandom(16)
client_cipher = Cipher(
    algorithm=algorithms.AES(key=client_shared_key),
    mode=modes.CBC(initialization_vector=iv),
)
encryptor = client_cipher.encryptor()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()


# Client sends encrypted message to server along with the initialization vector
# 3. client --- cipher, iv ---> server
received_ciphertext, received_iv = ciphertext, iv

server_cipher = Cipher(
    algorithm=algorithms.AES(key=server_shared_key),
    mode=modes.CBC(initialization_vector=received_iv),
)
decryptor = server_cipher.decryptor()
padded_decrypted_message = decryptor.update(received_ciphertext) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
decrypted_message = unpadder.update(padded_decrypted_message) + unpadder.finalize()
assert decrypted_message == MESSAGE_TO_SEND
