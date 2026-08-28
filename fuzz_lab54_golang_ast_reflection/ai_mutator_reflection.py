import random
import struct

REFL_MAGIC = 0x5245464C

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = REFL_MAGIC
    if random.random() < 0.6:
        method = b"DangerousSink"
    else:
        method = random.choice([b"SafeOp", b"InvalidMethod", b"String"])

    raw = struct.pack("<IB", magic, len(method)) + method
    return bytearray(raw[:max_size])

def deinit():
    pass
