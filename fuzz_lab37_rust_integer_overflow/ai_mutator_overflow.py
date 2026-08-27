import random
import struct

OVERFLOW_MAGIC = 0x4F56464C

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = OVERFLOW_MAGIC
    if random.random() < 0.6:
        op_type = 0xEE
        val_a = random.choice([0xFFFFFFF0, 0xFFFFFFFF, 0xFFFFFF50])
        val_b = random.randint(0x0100, 0xFFFF)
    else:
        op_type = 0x01
        val_a = random.randint(1, 1000)
        val_b = random.randint(1, 100)

    raw = struct.pack("<IBIH", magic, op_type, val_a, val_b)
    return bytearray(raw[:max_size])

def deinit():
    pass
