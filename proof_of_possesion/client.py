import os
from hashlib import sha256
from pathlib import Path

from rich import print

from challenge import agg_gen_challange
from file import compute_sha256_of
from generator import SubgroupGenerator
from mcl import G1, Fr
from my_types import ServerChallenge
from polynomial import agg_poly
from settings import NUMBER_OF_PAGES, PAGE_SIZE
from tag_block import tag_block
from upload import send_block_file, send_challange_and_wait_for_response

fr = Fr.rnd()
g = G1.hashAndMapTo(os.urandom(16))

subgroup_G = SubgroupGenerator(fr=fr, g=g)


block_index = 0
block_ids: list[bytes] = []
file_id = compute_sha256_of(file=Path("10mb_file"))

with open("10mb_file", mode="rb") as file:
    while (block_m := file.read(NUMBER_OF_PAGES * PAGE_SIZE)) != b"":
        block_id = sha256(block_m).digest()
        polynomial = agg_poly(subgroup=subgroup_G, block_id=block_id, file_id=file_id)
        tagged_blocks = tag_block(block_m=block_m, polynomial=polynomial)

        send_block_file(
            tagged_blocks=tagged_blocks,
            block_index=block_index,
            block_id=block_id.hex(),
        )
        block_index += 1
        block_ids.append(block_id)

# TODO: erase file here

kf, h_challenge = agg_gen_challange(
    subgroup=subgroup_G, blocks_ids=block_ids, file_id=file_id
)
print(f"kf: {kf}")

p = send_challange_and_wait_for_response(
    challange_for_server=ServerChallenge(
        g_r=h_challenge.g_r,
        x_c=h_challenge.x_c,
        g_r_poly0=h_challenge.g_r_poly0,
        block_ids=[block.hex() for block in block_ids],
    )
)
assert p == kf
