from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from person import Person

ec.ECDSA

client = Person()
signature = client.secret_key.sign(
    data=b"Super secret message to sign  ecc private key",
    signature_algorithm=ec.ECDSA(hashes.SHA256()),
)

client.public_key.verify(
    signature=signature,
    data=b"Super secret message to sign  ecc private key",
    signature_algorithm=ec.ECDSA(hashes.SHA256()),
)
