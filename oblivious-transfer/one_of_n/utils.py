def xor_bytes(ba1: bytes, ba2: bytes) -> bytes:
    """
    XORs two byte arrays of equal length
    """
    assert len(ba1) == len(ba2), f"XOR {len(ba1)=} != {len(ba2)=}"

    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])


def xor_all_elements(elements: list[bytes]) -> bytes:
    result = elements[0]
    for element in elements[1:]:
        result = xor_bytes(ba1=result, ba2=element)
    return result
