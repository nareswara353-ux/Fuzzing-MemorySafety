import random
import struct

PROTO_MAGIC = 0x50525442

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = PROTO_MAGIC
    if random.random() < 0.6:
        tag = 0xDF
        payload = b"MALFORMED_VARINT_BYTES" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        tag = random.choice([0x01, 0x02, 0x10])
        payload = bytearray(random.getrandbits(8) for _ in range(16))

    body = struct.pack("<IB", magic, tag) + bytes(payload)
    msg_len = len(body)
    flag = 0x00
    frame = struct.pack(">BI", flag, msg_len) + body

    return bytearray(frame[:max_size])

def deinit():
    pass
