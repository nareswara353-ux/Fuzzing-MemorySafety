import random
import struct

RUST_MAGIC = 0x54535552

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = RUST_MAGIC
    if random.random() < 0.6:
        cmd = 0xAA
        payload = b"UNSAFE_EXPLOIT" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        cmd = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    length = len(payload)
    raw = struct.pack("<IBH", magic, cmd, length) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
