import random
import struct

PKL_MAGIC = b"PKL\x00"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        opcode = 0xFE
        payload = b"CRITICAL_PICKLE_EXEC_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        opcode = random.choice([0x01, 0x02])
        if opcode == 0x01:
            payload = struct.pack("<I", random.randint(0, 65535))
        else:
            payload = b"SAFE_DATA_STRING"

    raw = PKL_MAGIC + struct.pack("B", opcode) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
