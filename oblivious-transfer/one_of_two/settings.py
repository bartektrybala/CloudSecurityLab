HOST = "0.0.0.0"
PORT = 12345
BUFFER_SIZE = 2048

PUBLIC_KEY_PREFIX = b"##PUBLIC_KEY_PREFIX#"
EK0_AND_EK1_PREFIX = b"#EK0_AND_EK1_PREFIX#"
FINISH_PROTOCOL_PREFIX = b"####FINISH_P_PREFIX#"

assert len(PUBLIC_KEY_PREFIX) == len(EK0_AND_EK1_PREFIX) == len(FINISH_PROTOCOL_PREFIX)
PREFIX_FIXED_SIZE = len(PUBLIC_KEY_PREFIX)