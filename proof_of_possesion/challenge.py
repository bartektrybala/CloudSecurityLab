from file import find_block_file, load_tagged_blocks_from_disc
from generator import SubgroupGenerator
from mcl.structures.Fr import Fr
from mcl.structures.G1 import G1
from my_types import H_challenge, ServerChallenge, TaggedBlock
from polynomial import agg_poly


def agg_gen_challange(
    subgroup: SubgroupGenerator, blocks_ids: list[str], file_id: str
) -> tuple[G1, H_challenge]:
    g = subgroup.g
    poly0 = agg_poly(subgroup=subgroup, block_id=file_id, file_id=file_id)

    r = subgroup.random_element()
    x_c = subgroup.random_element()
    # WARNING: x_c should be different from 0 and from any of the subblocks
    # of the block_m, but as file is erased after upload, we can't check that

    kf = sum(
        [
            g
            * (r * agg_poly(subgroup=subgroup, block_id=block_id, file_id=file_id)(x_c))
            for block_id in blocks_ids
        ],
        start=G1(),
    )
    h = H_challenge(
        g_r=g * r,
        x_c=x_c,
        g_r_poly0=g * (r * poly0(Fr())),
    )
    return kf, h


def prepare_data_for_interpolation(
    tagged_blocks: list[TaggedBlock], g_r: G1, g_r_poly0: G1
) -> list[tuple[Fr, G1]]:
    point_0 = (Fr(), g_r_poly0)
    pairs_of_points = [point_0]

    for subblock_bytes, tag in tagged_blocks:
        m = Fr()
        m.setInt(int.from_bytes(subblock_bytes))
        point = m, g_r * tag
        pairs_of_points.append(point)

    return pairs_of_points


def interpolate_polynomial_in_exponent(
    pairs_of_points: list[tuple[Fr, G1]], x: Fr
) -> G1:
    result = G1()
    for i, (x_i, y_i) in enumerate(pairs_of_points):
        numerator = Fr()
        numerator.setInt(1)

        denominator = Fr()
        denominator.setInt(1)

        for j, (x_j, _) in enumerate(pairs_of_points):
            if i == j:
                continue
            numerator *= x - x_j
            denominator *= x_i - x_j
        result += y_i * (numerator / denominator)
    return result


def agg_gen_proof(server_challenge: ServerChallenge) -> G1:
    print("Generating proof...")

    result = G1()

    for block_id in server_challenge.block_ids:
        block_path = find_block_file(block_id=block_id)
        tagged_blocks = load_tagged_blocks_from_disc(path=block_path)

        pairs_of_points = prepare_data_for_interpolation(
            tagged_blocks=tagged_blocks,
            g_r=server_challenge.g_r,
            g_r_poly0=server_challenge.g_r_poly0,
        )
        result += interpolate_polynomial_in_exponent(
            pairs_of_points=pairs_of_points, x=server_challenge.x_c
        )
    return result
