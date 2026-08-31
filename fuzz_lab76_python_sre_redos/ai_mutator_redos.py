import random

SAFE_EMAILS = [
    b"user@example.com",
    b"admin.test@domain.org",
    b"support123@service.co.id"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"REDOS_EXPLOIT_PATTERN_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = random.choice(SAFE_EMAILS)

    return bytearray(payload[:max_size])

def deinit():
    pass
