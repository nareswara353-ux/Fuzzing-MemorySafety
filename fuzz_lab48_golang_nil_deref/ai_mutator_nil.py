import random
import struct

NIL_MAGIC = 0x4E494C50

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = NIL_MAGIC
    if random.random() < 0.6:
        type_tag = 0xEE
        payload = b"NIL_TRIGGER" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        type_tag = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<IB", magic, type_tag) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
