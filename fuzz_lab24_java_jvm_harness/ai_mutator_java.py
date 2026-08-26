import random
import struct

JAVA_MAGIC = 0x4156414A # 'JAVA'

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = JAVA_MAGIC
    cmd = random.choice([0x01, 0x02, 0x7F])

    if random.random() < 0.6:
        # Injeksi payload pemicu exception fatal JVM
        payload = b"UNCAUGHT_JVM_EXCEPTION_TRIGGER" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    length = len(payload)
    raw = struct.pack("<IHH", magic, cmd, length) + bytes(payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
