import random

SAFE_THREAD_COMMANDS = [
    b"SAFE_CONCURRENT_TASK_1",
    b"PARALLEL_CALCULATION_OK",
    b"THREAD_POOL_NORMAL"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"TRIGGER_GIL_DEADLOCK_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = random.choice(SAFE_THREAD_COMMANDS)

    return bytearray(payload[:max_size])

def deinit():
    pass
