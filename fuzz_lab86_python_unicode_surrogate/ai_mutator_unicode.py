import random
import struct

UNI_MAGIC = b"UNI\x00"
HEADER_FORMAT = "<4sHH"

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Generate lone surrogate UTF-8 sequence (U+D800 -> \xED\xA0\x80)
        enc_flag = 1
        payload = b"\xed\xa0\x80" + b"TRIGGER_UNICODE_CRASH_" + bytearray(random.getrandbits(8) for _ in range(8))
    else:
        enc_flag = 0
        payload = b"SAFE_UTF8_UNICODE_STRING_" + str(random.randint(100, 999)).encode("utf-8")

    header = struct.pack(HEADER_FORMAT, UNI_MAGIC, enc_flag, len(payload))
    raw = header + payload
    return bytearray(raw[:max_size])

def deinit():
    pass
