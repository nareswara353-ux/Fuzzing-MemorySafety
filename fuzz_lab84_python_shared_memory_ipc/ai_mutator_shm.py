import random
import struct

SHM_MAGIC = b"SHM\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        offset = random.randint(40, 100)
        length = random.randint(30, 128)
        payload = b"TRIGGER_SHM_OOB_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        offset = 0
        length = 16
        payload = b"SAFE_IPC_DATA_16"

    header = struct.pack(HEADER_FORMAT, SHM_MAGIC, offset, length)
    raw = header + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
