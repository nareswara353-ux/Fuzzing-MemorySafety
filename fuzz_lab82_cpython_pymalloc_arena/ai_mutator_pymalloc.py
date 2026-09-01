import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        alloc_size = 64
        write_len = random.randint(128, 512)
        payload = b"TRIGGER_PYMALLOC_CORRUPTION_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        alloc_size = 64
        write_len = 32
        payload = b"SAFE_PYMALLOC_PAYLOAD_STRING"

    raw = struct.pack("<ii", alloc_size, write_len) + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
