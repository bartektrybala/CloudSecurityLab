import hashlib
import pickle
from pathlib import Path
from typing import cast

from my_types import TaggedBlock
from settings import PAGE_SIZE


def compute_sha256_of(file: Path) -> bytes:
    hash_sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(PAGE_SIZE), b""):
            hash_sha256.update(chunk)
    return hash_sha256.digest()


def find_block_file(block_id: str) -> Path:
    for block_file in Path("server_file").glob(f"**/{block_id}"):
        return block_file


def load_tagged_blocks_from_disc(path: Path) -> list[TaggedBlock]:
    with open(path, "rb") as file:
        tagged_blocks_data = file.read()
    return cast(list[TaggedBlock], pickle.loads(tagged_blocks_data))
