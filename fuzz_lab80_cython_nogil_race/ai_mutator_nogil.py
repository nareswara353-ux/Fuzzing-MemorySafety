import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        offset = random.randint(500, 20000)
        payload = b"TRIGGER_NOGIL_RACE_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        offset = random.randint(0, 30)
        payload = b"SAFE_NOGIL_EXECUTION_TASK"

    raw = struct.pack("<i", offset) + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
