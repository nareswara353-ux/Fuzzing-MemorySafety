import random
import struct

STREAM_MAGIC = 0x5354524D

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = STREAM_MAGIC
    if random.random() < 0.6:
        cmd = 0xBB
        chunk_count = random.randint(600, 2000)
        payload = b"BACKPRESSURE_SATURATION_BURST" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        cmd = 0x01
        chunk_count = random.randint(1, 100)
        payload = b"SAFE_STREAM_CHUNKS"

    raw = struct.pack("<IBH", magic, cmd, chunk_count) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
