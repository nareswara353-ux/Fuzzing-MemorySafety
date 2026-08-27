import random
import struct

GO_MAGIC = 0x474F4C47

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = GO_MAGIC
    if random.random() < 0.6:
        cmd = 0xAA
        payload = b"PANICGO" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        cmd = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IB", magic, cmd) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
