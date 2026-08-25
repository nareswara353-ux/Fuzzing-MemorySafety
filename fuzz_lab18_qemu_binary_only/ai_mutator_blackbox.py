import random
import struct

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    if len(mutated) < 48:
        mutated.extend(b"\x00" * (48 - len(mutated)))

    # Pasang Magic 'BIN$'
    mutated[0:4] = b"BIN$"
    # Pasang Secret Key (0x4B4C4142)
    mutated[4:8] = struct.pack("<I", 0x4B4C4142)
    # Pasang Payload Length
    mutated[8:12] = struct.pack("<I", 36)

    # 50% injeksi token CORE
    if random.random() < 0.5:
        mutated[12:16] = b"CORE"
    else:
        mutated[12] = (mutated[12] + 1) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
