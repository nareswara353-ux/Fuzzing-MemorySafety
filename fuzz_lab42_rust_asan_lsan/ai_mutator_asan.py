import random
import struct

ASAN_MAGIC = 0x4153414E

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = ASAN_MAGIC
    if random.random() < 0.6:
        mode = 0xAA
        payload = b"ASAN_TRIGGER" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        mode = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IB", magic, mode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
