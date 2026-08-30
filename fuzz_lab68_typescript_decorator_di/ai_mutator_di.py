import json
import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload_dict = {
            "serviceToken": "SystemExec",
            "contextId": random.randint(1000, 9999)
        }
    else:
        payload_dict = {
            "serviceToken": random.choice(["SafeLogger", "UnknownToken", "AuthService"]),
            "contextId": random.randint(1, 100)
        }

    raw = json.dumps(payload_dict).encode("utf-8")
    return bytearray(raw[:max_size])

def deinit():
    pass
