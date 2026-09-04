import random
import struct

WASM_MAGIC = b"\x00asm"
WASM_VERSION = 1
HEADER_FORMAT = "<4sIHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Generate boundary edge-cases: near 64KB boundary with special value
        opcode = 0x28  # i32.load
        offset = 0xFFFC  # Bound edge triggering differential divergence
        value = 0xDEADBEEF
        extra = b"TRIGGER_TIER_DIVERGENCE_" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        opcode = random.choice([0x28, 0x36])
        offset = random.randint(0, 1024)
        value = random.randint(100, 50000)
        extra = b"SAFE_WASM_BYTECODE_PAYLOAD"

    header = struct.pack(HEADER_FORMAT, WASM_MAGIC, WASM_VERSION, opcode, offset)
    val_bytes = struct.pack("<I", value)
    raw = header + val_bytes + extra
    return bytearray(raw[:max_size])

def deinit():
    pass
