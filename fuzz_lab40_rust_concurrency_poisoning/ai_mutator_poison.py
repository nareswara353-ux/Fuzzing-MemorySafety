import random
import struct

POISON_MAGIC = 0x504F4953

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = POISON_MAGIC
    if random.random() < 0.6:
        mode = 0xDD
        payload = b"POISON_MUTEX_TRIGGER" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        mode = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IB", magic, mode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
