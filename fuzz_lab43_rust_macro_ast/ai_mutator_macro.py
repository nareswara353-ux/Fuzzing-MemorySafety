import random
import struct

MACRO_MAGIC = 0x4D414352

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = MACRO_MAGIC
    if random.random() < 0.6:
        token_type = 0xFE
        depth = random.randint(55, 100)
        payload = b"EXPAND_BOMB" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        token_type = random.choice([0x01, 0x02, 0x10])
        depth = random.randint(1, 10)
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IBB", magic, token_type, depth) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
