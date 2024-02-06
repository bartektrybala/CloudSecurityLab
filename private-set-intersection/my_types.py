from typing import NamedTuple

import mcl


class ClientAndServerBlindedSets(NamedTuple):
    client_set: list[mcl.G1]
    server_set: list[mcl.Fr]
