import random
import struct

JNI_MAGIC = 0x494e4a24

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = JNI_MAGIC
    if random.random() < 0.6:
        sub_cmd = 0xdeadc0de
        payload = b"OVERFLOW_TRIGGER" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        sub_cmd = random.randint(0, 0xFFFFFFFF)
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    raw = struct.pack("<II", magic, sub_cmd) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
