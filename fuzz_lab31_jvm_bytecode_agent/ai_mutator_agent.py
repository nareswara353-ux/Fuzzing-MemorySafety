import struct
import random

AGENT_MAGIC = 0x41474e54

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = AGENT_MAGIC
    if random.random() < 0.6:
        opcode = 0x77
        payload = b"Z" + bytearray(random.getrandbits(8) for _ in range(15))
    else:
        opcode = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<II", magic, opcode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
