from collections import namedtuple

TaggedBlock = namedtuple("TaggedBlock", ["m", "t"])
H_challenge = namedtuple("H_challenge", ["g_r", "x_c", "g_r_poly0"])
ServerChallenge = namedtuple(
    "ServerChallenge", ["g_r", "x_c", "g_r_poly0", "block_ids"]
)
