import random
import struct

GCC_MAGIC = b"GCC\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        gen_target = random.randint(0, 2)
        flags = 0xDEAD
        payload = b"TRIGGER_GC_SINK_" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        gen_target = random.randint(0, 2)
        flags = 0x0001
        payload = b"SAFE_CYCLIC_DATA_STREAM"

    header = struct.pack(HEADER_FORMAT, GCC_MAGIC, gen_target, flags)
    raw = header + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
