import json
import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = {
            "tasks": [
                {"id": 1, "duration_ms": 10, "blocking": False},
                {"id": 2, "duration_ms": 600, "blocking": True},
                {"id": 3, "duration_ms": 20, "blocking": False}
            ]
        }
    else:
        payload = {
            "tasks": [
                {"id": 1, "duration_ms": 10, "blocking": False},
                {"id": 2, "duration_ms": 15, "blocking": False}
            ]
        }

    raw = json.dumps(payload).encode("utf-8")
    return bytearray(raw[:max_size])

def deinit():
    pass
