from mcl import Fr
from my_types import TaggedBlock
from polynomial import Polynomial
from settings import NUMBER_OF_PAGES


def subblocks_of(block: bytes, size: int) -> list[bytes]:
    subblocks = []
    subblock_size = len(block) // size

    for i in range(size):
        if i == size - 1:
            # last subblock is the remaining bytes
            subblocks.append(block[i * subblock_size :])
        else:
            subblocks.append(block[i * subblock_size : (i + 1) * subblock_size])
    return subblocks


def tag_block(
    block_m: bytes,
    polynomial: Polynomial,
    z: int = NUMBER_OF_PAGES,
) -> list[TaggedBlock]:
    """
    Returns a list of tagged blocks.
    Each tagged block is a tuple of the form (m, t) where:
        - m is a block of the message
        - t is a tag for the block
    """

    tagged_blocks = []
    counter = 0
    for subblock_bytes in subblocks_of(block=block_m, size=z):
        m = Fr()
        m.setInt(int.from_bytes(subblock_bytes))
        tagged_blocks.append(TaggedBlock(m=subblock_bytes, t=polynomial(m)))
        counter += 1
    return tagged_blocks
