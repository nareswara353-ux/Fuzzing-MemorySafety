import random
import struct

H2_MAGIC = 0x48325354

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = H2_MAGIC
    if random.random() < 0.6:
        stream_count = random.randint(50, 200)
        reset_count = stream_count + random.randint(10, 100)
        flags = 0x52
        payload = b"RAPID_RESET_BURST" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        stream_count = random.randint(1, 5)
        reset_count = 0
        flags = 0x01
        payload = b"STANDARD_H2_STREAM"

    raw = struct.pack("<IBHB", magic, stream_count, reset_count, flags) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
