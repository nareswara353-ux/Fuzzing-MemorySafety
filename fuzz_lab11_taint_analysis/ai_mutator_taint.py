import os
import struct
import random

TAINT_FILE = "/tmp/tainted_offsets.bin"

def init(seed):
    random.seed(seed)

def read_tainted_indices():
    if not os.path.exists(TAINT_FILE):
        return [20, 21, 22, 23]
    try:
        with open(TAINT_FILE, "rb") as f:
            data = f.read()
            if len(data) >= 128:
                mask = data[:128]
                active = [i for i, b in enumerate(mask) if b == 1]
                return active if active else [20, 21, 22, 23]
    except Exception:
        pass
    return [20, 21, 22, 23]

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    if len(mutated) < 24:
        mutated.extend(b"\x00" * (24 - len(mutated)))

    # 1. Kunci struktur invariant kritis yang telah lolos analisis
    mutated[0:4] = b"DTA!"
    mutated[8:10] = b"AA"
    mutated[16:20] = struct.pack("<I", 0x1337C0DE)

    # 2. Taint-guided mutation difokuskan pada payload bebas di luar invariant header
    if len(mutated) > 20:
        target_idx = random.randint(20, len(mutated) - 1)
        mutated[target_idx] = (mutated[target_idx] + 1) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
