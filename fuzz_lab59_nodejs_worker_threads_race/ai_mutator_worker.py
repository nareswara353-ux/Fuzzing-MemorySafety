import json
import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload_dict = {
            "mode": "RACE_TRIGGER",
            "threads": 2,
            "increments": 500
        }
    else:
        payload_dict = {
            "mode": "SAFE_MODE",
            "threads": 1,
            "increments": 10
        }

    raw = json.dumps(payload_dict).encode("utf-8")
    return bytearray(raw[:max_size])

def deinit():
    pass
