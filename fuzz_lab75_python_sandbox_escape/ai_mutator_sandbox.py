import random

SAFE_EXPRESSIONS = [
    b"1 + 1",
    b"[x for x in range(10)]",
    b"len('test_string')",
    b"{'key': 'value'}"
]

ESCAPE_PAYLOADS = [
    b"().__class__.__base__.__subclasses__()",
    b"[].__class__.__base__.__subclasses__()",
    b"''.__class__.__mro__[1].__subclasses__()",
    b"().__class__.__base__.__subclasses__()[137].__init__.__globals__['__builtins__']"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = random.choice(ESCAPE_PAYLOADS)
    else:
        payload = random.choice(SAFE_EXPRESSIONS)

    return bytearray(payload[:max_size])

def deinit():
    pass
