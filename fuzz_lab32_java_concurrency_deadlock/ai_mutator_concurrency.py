import struct
import random

THREAD_MAGIC = 0x54485244

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = THREAD_MAGIC
    if random.random() < 0.6:
        mode = 0xDEAD
        payload = b"DEADLOCK_TEST" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        mode = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<II", magic, mode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
