import random
import struct

CGO_MAGIC = 0x43474F21

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = CGO_MAGIC
    if random.random() < 0.6:
        cmd = 0xCC
        payload = b"CGO_CORRUPT" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        cmd = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IB", magic, cmd) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
