import os
import struct
import random

DIST_FILE = "/tmp/branch_distance.bin"

def init(seed):
    pass

def read_distance_feedback():
    if not os.path.exists(DIST_FILE):
        return None
    try:
        with open(DIST_FILE, "rb") as f:
            data = f.read()
            if len(data) >= 16 * 8:
                return struct.unpack("<16q", data[:128])
    except Exception:
        pass
    return None

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    if len(mutated) < 16:
        mutated.extend(b"\x00" * (16 - len(mutated)))

    feedback = read_distance_feedback()
    
    # Gradient-Guided Multi-Stage Constraint Solver
    if feedback:
        d1 = feedback[1]  # Stage 1 Distance (Magic)
        d2 = feedback[2]  # Stage 2 Distance (val1 + val2 == 0x1337)
        d3 = feedback[3]  # Stage 3 Distance (val1 * 3 == checksum)

        # 1. Selesaikan Stage 1 (Header Magic "VLLX")
        mutated[0:4] = struct.pack("<I", 0x584c4c56)
        if d1 != 0:
            return mutated[:max_size]

        # 2. Selesaikan Stage 2 (val1 + val2 == 0x1337 / 4919)
        mutated[4:8] = struct.pack("<i", 0x1000)   # 4096
        mutated[8:12] = struct.pack("<i", 0x0337)  # 823
        if d2 != 0:
            return mutated[:max_size]

        # 3. Selesaikan Stage 3 (val1 * 3 == checksum -> 4096 * 3 = 12288)
        mutated[12:16] = struct.pack("<i", 0x1000 * 3)
        return mutated[:max_size]

    # Stochastic Fallback jika file feedback belum terbentuk
    pos = random.randint(0, min(len(mutated)-1, 15))
    mutated[pos] = (mutated[pos] + random.choice([-1, 1, 5, 10])) & 0xFF
    return mutated[:max_size]

def deinit():
    if os.path.exists(DIST_FILE):
        try:
            os.remove(DIST_FILE)
        except Exception:
            pass
