import random
import struct

NMP_MAGIC = b"NMP\x00"
HEADER_FORMAT = "<4sHHHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Generate invalid shape and strides out-of-bounds configuration
        rows = random.randint(4, 10)
        cols = random.randint(4, 10)
        stride_row = random.randint(10, 50)
        stride_col = random.randint(4, 20)
        payload = b"CORRUPT_STRIDES_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        # Valid 4x4 matrix fitting inside 32 bytes (element size = 2)
        rows = 4
        cols = 4
        stride_row = 8
        stride_col = 2
        payload = b"SAFE_CONTIGUOUS_ARRAY_PAYLOAD_32"

    payload_32 = payload[:32].ljust(32, b"\x00")
    raw = struct.pack(HEADER_FORMAT, NMP_MAGIC, rows, cols, stride_row, stride_col) + payload_32
    return bytearray(raw[:max_size])

def deinit():
    pass
