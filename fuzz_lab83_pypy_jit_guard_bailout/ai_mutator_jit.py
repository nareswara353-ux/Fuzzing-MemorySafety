import random
import struct

JIT_MAGIC = b"JIT\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        loop_iters = random.randint(100, 500)
        guard_type = 0xDEAD
        payload = b"TRIGGER_GUARD_FAIL_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        loop_iters = random.randint(10, 80)
        guard_type = 0x0001
        payload = b"SAFE_JIT_OPTIMIZED_STREAM"

    raw = struct.pack(HEADER_FORMAT, JIT_MAGIC, loop_iters, guard_type) + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
