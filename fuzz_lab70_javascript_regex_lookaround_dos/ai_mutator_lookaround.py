import random

SAFE_PASSWORDS = [
    b"ValidPass123!",
    b"AdminSecure#2026",
    b"StandardUser$88"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"LOOKAROUND_DOS_EXPLOIT_" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = random.choice(SAFE_PASSWORDS)

    return bytearray(payload[:max_size])

def deinit():
    pass
