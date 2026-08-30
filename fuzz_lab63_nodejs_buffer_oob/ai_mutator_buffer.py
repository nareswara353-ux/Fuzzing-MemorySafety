import random
import struct

BUFF_MAGIC = 0x42554646

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = BUFF_MAGIC
    if random.random() < 0.6:
        cmd = 0xEE
        offset = random.choice([-1, -100, 16, 500, 0x7FFFFFFF])
        payload = b"OOB_PAYLOAD" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        cmd = 0x01
        offset = random.randint(0, 15)
        payload = b"SAFE_DATA"

    raw = struct.pack("<IBi", magic, cmd, offset) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
