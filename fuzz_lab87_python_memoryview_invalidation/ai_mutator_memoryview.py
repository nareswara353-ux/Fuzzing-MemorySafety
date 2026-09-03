import random
import struct

MVW_MAGIC = b"MVW\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        action_flag = 0xDEAD
        offset = random.randint(200, 5000)
        payload = b"TRIGGER_BUFFER_INVALIDATION_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        action_flag = 0x0001
        offset = random.randint(0, 32)
        payload = b"SAFE_BUFFER_VIEW_DATA"

    header = struct.pack(HEADER_FORMAT, MVW_MAGIC, action_flag, offset)
    raw = header + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
