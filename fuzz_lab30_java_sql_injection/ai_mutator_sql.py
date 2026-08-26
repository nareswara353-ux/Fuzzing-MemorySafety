import random

SQL_PAYLOADS = [
    "' OR '1'='1",
    "admin' --",
    "' UNION SELECT null, username, password FROM users --",
    "' OR 1=1 --",
    "john_doe",
    "alice.smith"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.7:
        payload = random.choice(SQL_PAYLOADS)
    else:
        prefix = random.choice(["user", "admin", "test"])
        suffix = random.choice(["' OR 1=1", "'--", "123"])
        payload = f"{prefix}_{suffix}"
    
    return bytearray(payload.encode("utf-8")[:max_size])

def deinit():
    pass
