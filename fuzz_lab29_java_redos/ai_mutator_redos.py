import random

PATTERNS = [
    "a" * 25 + "!",
    "user" + "1" * 30 + "_",
    "admin_test_account",
    "a" * 40 + "@b"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.7:
        repeat_char = random.choice(["a", "b", "c", "1", "_"])
        length = random.randint(22, 35)
        suffix = random.choice(["!", "$", "%", "#", " "])
        payload = (repeat_char * length + suffix).encode("utf-8")
    else:
        payload = random.choice(PATTERNS).encode("utf-8")
    return bytearray(payload[:max_size])

def deinit():
    pass
