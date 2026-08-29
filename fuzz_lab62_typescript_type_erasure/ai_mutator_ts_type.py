import json
import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload_dict = {
            "userId": 999,
            "transactions": None  # Type Confusion: Null instead of Array
        }
    else:
        payload_dict = {
            "userId": 101,
            "transactions": [150, 200, 350]
        }

    raw = json.dumps(payload_dict).encode("utf-8")
    return bytearray(raw[:max_size])

def deinit():
    pass
