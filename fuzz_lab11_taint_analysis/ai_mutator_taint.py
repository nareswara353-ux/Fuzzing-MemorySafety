import os
import struct
import random

TAINT_FILE = "/tmp/tainted_offsets.bin"

def init(seed):
    pass

def read_tainted_indices():
    if not os.path.exists(TAINT_FILE):
        return [0, 1, 2, 3, 8, 9, 16, 17, 18, 19]
    try:
        with open(TAINT_FILE, "rb") as f:
            data = f.read()
            if len(data) >= 128:
                mask = data[:128]
                active_indices = [i for i, b in enumerate(mask) if b == 1]
                return active_indices if active_indices else [0, 8, 16]
    except Exception:
        pass
    return [0, 1, 2, 3, 8, 9, 16, 17, 18, 19]

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    if len(mutated) < 24:
        mutated.extend(b"\x00" * (24 - len(mutated)))

    # 1. Pasang header tetap
    mutated[0:4] = b"DTA!"
    # 2. Pasang command valid
    mutated[8:10] = b"AA"
    # 3. Pasang target key
    mutated[16:20] = struct.pack("<I", 0x1337C0DE)

    # Taint-Guided Mutation pada sisa byte yang terlacak
    tainted = read_tainted_indices()
    if tainted:
        target_idx = random.choice(tainted)
        if target_idx < len(mutated):
            mutated[target_idx] = (mutated[target_idx] + random.choice([0, 1, -1])) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
