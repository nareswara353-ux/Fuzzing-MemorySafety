import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = b"FIRM"
    device_id = 0x00010002 # Fixed target UUID
    cmd = random.choice([0x01, 0x02, 0xEE])
    
    if random.random() < 0.6:
        data_len = random.choice([24, 32, 48, 64])
    else:
        data_len = random.randint(1, 16)

    payload = bytearray(random.getrandbits(8) for _ in range(64))
    raw_packet = struct.pack("<4sIBH64s", magic, device_id, cmd, data_len, bytes(payload))

    return raw_packet[:max_size]

def deinit():
    pass
