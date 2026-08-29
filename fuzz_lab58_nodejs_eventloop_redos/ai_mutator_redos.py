import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"CRITICAL_EVENTLOOP_BLOCK_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = b"a" * random.randint(1, 10)

    return bytearray(payload[:max_size])

def deinit():
    pass
