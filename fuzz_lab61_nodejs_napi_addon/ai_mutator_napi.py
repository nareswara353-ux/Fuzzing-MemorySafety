import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"CRASH_NAPI_OVERFLOW_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = b"SAFE_NAPI_DATA_" + str(random.randint(100, 999)).encode("utf-8")

    return bytearray(payload[:max_size])

def deinit():
    pass
