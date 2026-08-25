import random
import struct

DRIVER_MAGIC = 0x88
COMMANDS = [0x01, 0x02, 0x03]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    # Struktur: magic (1B), cmd (1B), data_len (2B), payload (64B)
    magic = DRIVER_MAGIC
    cmd = random.choice(COMMANDS)
    
    # 50% probabilitas menguji integer overflow / buffer boundary di data_len
    if random.random() < 0.5:
        data_len = random.choice([32, 64, 128])
    else:
        data_len = random.randint(1, 16)

    payload = bytearray(random.getrandbits(8) for _ in range(64))
    
    raw_pkt = struct.pack("<BBH64s", magic, cmd, data_len, bytes(payload))
    return raw_pkt[:max_size]

def deinit():
    pass
