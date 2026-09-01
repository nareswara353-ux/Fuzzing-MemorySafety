import random

SAFE_INPUTS = [
    b"{'status': 'ok', 'code': 200}",
    b"[1, 2, 3, 4, 5]",
    b"('test', 123)",
    b"'plain_literal_string'"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = b"DANGEROUS_AST_PAYLOAD_" + bytearray(random.getrandbits(8) for _ in range(12))
    else:
        payload = random.choice(SAFE_INPUTS)

    return bytearray(payload[:max_size])

def deinit():
    pass
