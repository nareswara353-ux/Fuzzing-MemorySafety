import random
import struct

EXC_MAGIC = b"EXC\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        depth = random.randint(30, 80)
        flags = 0xDEAD
        payload = b"TRIGGER_UNWIND_PANIC_" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        depth = random.randint(1, 10)
        flags = 0x0001
        payload = b"SAFE_CALL_STACK_FLOW"

    header = struct.pack(HEADER_FORMAT, EXC_MAGIC, depth, flags)
    raw = header + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
