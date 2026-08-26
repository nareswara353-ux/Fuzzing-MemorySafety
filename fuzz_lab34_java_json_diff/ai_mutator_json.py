import random

DUPLICATE_KEY_TEMPLATES = [
    '{"role":"guest","role":"admin"}',
    '{"user":"alice","user":"root"}',
    '{"status":/*comment*/"active","role":"admin"}',
    '{"admin":false,"admin":true}',
    '{"id":100,"id":200}'
]

VALID_JSON = [
    '{"user":"john","role":"member"}',
    '{"status":"ok","code":200}'
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.7:
        payload = random.choice(DUPLICATE_KEY_TEMPLATES)
    else:
        payload = random.choice(VALID_JSON)
    return bytearray(payload.encode("utf-8")[:max_size])

def deinit():
    pass
