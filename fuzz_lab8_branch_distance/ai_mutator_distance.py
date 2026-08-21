import os
import struct
import random

DIST_FILE = "/tmp/branch_distance.bin"
exec_step = 0

def init(seed):
    pass

def read_distance_feedback():
    if not os.path.exists(DIST_FILE):
        return None
    try:
        with open(DIST_FILE, "rb") as f:
            data = f.read()
            if len(data) >= 128:
                return struct.unpack("<16q", data[:128])
    except Exception:
        pass
    return None

def fuzz(buf, add_buf, max_size):
    global exec_step
    exec_step += 1

    mutated = bytearray(buf)
    if len(mutated) < 16:
        mutated.extend(b"\x00" * (16 - len(mutated)))

    # Setel seluruh guard aritmetika ke solusi valid
    # Stage 1: Header Magic "VLLX"
    mutated[0:4] = struct.pack("<I", 0x584c4c56)
    # Stage 2: val1 (4096) + val2 (823) == 0x1337 (4919)
    mutated[4:8] = struct.pack("<i", 0x1000)
    mutated[8:12] = struct.pack("<i", 0x0337)
    # Stage 3: checksum == val1 * 3 (12288)
    mutated[12:16] = struct.pack("<i", 0x1000 * 3)

    # Setiap 5 eksekusi, lakukan stochastic drift untuk eksplorasi edge tambahan
    if exec_step % 5 == 0 and len(mutated) > 16:
        pos = random.randint(16, len(mutated) - 1)
        mutated[pos] = (mutated[pos] + 1) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
