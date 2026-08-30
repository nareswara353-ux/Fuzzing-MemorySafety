import random
import struct

WASM_MAGIC = 0x5741534D

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = WASM_MAGIC
    if random.random() < 0.6:
        cmd = 0xAA
        offset = random.choice([-1, -1024, 65536, 70000, 0x7FFFFFFF])
        payload = b"WASM_OOB_BURST" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        cmd = 0x01
        offset = random.randint(0, 65535)
        payload = b"SAFE_WASM"

    raw = struct.pack("<IBi", magic, cmd, offset) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
