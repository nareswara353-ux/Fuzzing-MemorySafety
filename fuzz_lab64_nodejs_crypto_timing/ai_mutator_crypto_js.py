import random
import struct

CRYPTO_MAGIC = 0x4A534352
SECRET_TOKEN = b"NODEJS_CRYPTO_TIMING_SECRET_KEY"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = CRYPTO_MAGIC
    if random.random() < 0.6:
        mode = 0xCC
        payload = SECRET_TOKEN
    else:
        mode = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(32))

    raw = struct.pack("<IB", magic, mode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
