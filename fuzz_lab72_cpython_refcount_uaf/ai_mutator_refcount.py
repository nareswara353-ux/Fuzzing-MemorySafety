import random

SAFE_PAYLOADS = [
    b"SAFE_PAYLOAD_100",
    b"REGULAR_INPUT_STREAM",
    b"VALID_CPYTHON_DATA"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"TRIGGER_UAF_DECREF_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = random.choice(SAFE_PAYLOADS)

    return bytearray(payload[:max_size])

def deinit():
    pass
