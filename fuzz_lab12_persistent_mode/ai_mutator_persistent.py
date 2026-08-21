import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    if len(mutated) < 12:
        mutated.extend(b"\x00" * (12 - len(mutated)))

    # Pasang FAST header dan ukuran payload 4 byte
    mutated[0:4] = b"FAST"
    mutated[4:8] = struct.pack("<I", 4)

    # 40% kemungkinan menyuntikkan token BOOM
    if random.random() < 0.4:
        mutated[8:12] = b"BOOM"
    else:
        mutated[8] = (mutated[8] + 1) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
