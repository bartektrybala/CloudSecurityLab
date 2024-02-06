import mcl
import secrets
from typing import TypeVar


T = TypeVar("T")


def secure_shuffled(elements: list[T]) -> list[T]:
    return [
        elements.pop(secrets.randbelow(len(elements))) for _ in range(len(elements))
    ]


def encrypt_set(set_to_encrypt: list[mcl.G1], key: mcl.Fr) -> list[mcl.G1]:
    return [element * key for element in set_to_encrypt]


def hash_set_to_g1(set_to_hash: list[bytes]) -> list[mcl.G1]:
    return [mcl.G1.hashAndMapTo(element) for element in set_to_hash]


def hash_set_to_fr(set_to_hash: list[mcl.G1]) -> list[mcl.Fr]:
    set_serialized = [element.serialize() for element in set_to_hash]
    return [mcl.Fr.setHashOf(element) for element in set_serialized]


def decrypt_set(set_to_decrypt: list[mcl.G1], key: mcl.Fr) -> list[mcl.G1]:
    return [element * (~key) for element in set_to_decrypt]
