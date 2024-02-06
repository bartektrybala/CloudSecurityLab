from generator import SubgroupGenerator
from mcl.structures.Fr import Fr
from settings import NUMBER_OF_PAGES


class Polynomial:
    coefficients: list[Fr]

    def __init__(self, coefficients: list[Fr]) -> None:
        self.coefficients = coefficients

    def __call__(self, x: Fr) -> Fr:
        value = self.coefficients[-1]
        for coefficient in reversed(self.coefficients[:-1]):
            value = value * x + coefficient
        return value


def agg_poly(
    subgroup: SubgroupGenerator,
    block_id: bytes,
    file_id: bytes,
    z: int = NUMBER_OF_PAGES,
) -> Polynomial:
    """
    Returns a random polynomial of degree z with coefficients in Zq
    """

    coefficients = subgroup.generate_coefficients_for(
        block_id=block_id, file_id=file_id, z=z
    )
    return Polynomial(coefficients)
