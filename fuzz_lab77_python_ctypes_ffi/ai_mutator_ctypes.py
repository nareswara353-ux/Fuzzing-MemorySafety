import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload_id = 999
        length = 128
        data = b"TRIGGER_CTYPES_CORRUPTION_" + bytearray(random.getrandbits(8) for _ in range(6))
    else:
        payload_id = random.randint(1, 50)
        length = 16
        data = b"SAFE_DATA_STREAM"

    raw = struct.pack("<ii32s", payload_id, length, data)
    return bytearray(raw[:max_size])

def deinit():
    pass
