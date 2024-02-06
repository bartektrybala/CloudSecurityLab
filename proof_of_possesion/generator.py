from mcl import G1, Fr


class SubgroupGenerator:
    fr: Fr
    g: G1

    def __init__(self, fr: Fr, g: G1) -> None:
        self.fr = fr
        self.g = g

    def random_element(self) -> Fr:
        return Fr.rnd()

    def generate_coefficients_for(
        self, block_id: bytes, file_id: bytes, z: int
    ) -> list[Fr]:
        a_zero = Fr.setHashOf(self.fr.serialize() + file_id + b"0")
        seeded_fr = lambda i: Fr.setHashOf(
            self.fr.serialize() + block_id + str(i).encode("UTF-8")
        )
        return [a_zero] + [seeded_fr(i) for i in range(1, z)]
