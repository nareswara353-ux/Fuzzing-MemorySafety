import random
import struct

ZEROCOPY_MAGIC = 0x5A435059

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = ZEROCOPY_MAGIC
    if random.random() < 0.6:
        tag = 0x7E
        name = b"admin_zero"
        payload = b"CRITICAL_ZEROCOPY_PAYLOAD"
    else:
        tag = random.choice([0x01, 0x02, 0x10])
        name = random.choice([b"user", b"guest", b"client"])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    name_len = len(name)
    payload_len = len(payload)
    raw = struct.pack("<IBBH", magic, tag, name_len, payload_len) + name + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
