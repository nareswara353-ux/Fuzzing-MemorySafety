import random
import struct

WASM_MAGIC = b"\x00asm"
WASM_VERSION = b"\x01\x00\x00\x00"

SEC_TYPE = 0x01
SEC_FUNC = 0x03
SEC_CODE = 0x0A

OPCODES = [0x41, 0x6A, 0x10, 0x0B, 0x20, 0x21]

def init(seed):
    random.seed(seed)

def build_section(sec_id, content):
    return struct.pack("<BB", sec_id, len(content)) + content

def fuzz(buf, add_buf, max_size):
    # Layer 1: Header Biner WASM Baku
    wasm_header = WASM_MAGIC + WASM_VERSION

    # Layer 2: Valid Type & Function Section
    sec_type = build_section(SEC_TYPE, b"\x01\x60\x00\x00")
    sec_func = build_section(SEC_FUNC, b"\x01\x00")

    # Layer 3: Dynamic Code Section Mutation
    if random.random() < 0.6:
        # Suntikkan sequence bytecode pemicu JIT trap (0x41, 0x6a, 0x10)
        code_body = bytes([0x41, 0x6A, 0x10]) + bytearray(random.getrandbits(8) for _ in range(24))
    else:
        code_body = bytearray(random.choice(OPCODES) for _ in range(16))

    sec_code = build_section(SEC_CODE, code_body)

    module = wasm_header + sec_type + sec_func + sec_code
    return bytearray(module[:max_size])

def deinit():
    pass
