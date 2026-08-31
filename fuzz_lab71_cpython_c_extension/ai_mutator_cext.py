import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.7:
        # Generate long string to trigger overflow
        payload = b"A" * random.randint(256, 1024)
    else:
        payload = b"safe_input_" + str(random.randint(0, 100)).encode()
    
    return bytearray(payload[:max_size])

def deinit():
    pass
