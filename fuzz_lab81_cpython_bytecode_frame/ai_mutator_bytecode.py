import random
import struct

BCF_MAGIC = b"BCF\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Generate unbalanced stack underflow sequence (POP without LOAD)
        opcodes = b"\x01\x00\x01\x00\x01\x00" + b"STACK_UNDERFLOW_TRIGGER_" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        # Balanced sequence: LOAD_CONST (100, 0), LOAD_CONST (100, 1), POP_TOP (1, 0), POP_TOP (1, 0)
        opcodes = bytes([100, 0, 100, 1, 1, 0, 1, 0])

    header = struct.pack(HEADER_FORMAT, BCF_MAGIC, len(opcodes), 0)
    raw = header + opcodes
    return bytearray(raw[:max_size])

def deinit():
    pass
