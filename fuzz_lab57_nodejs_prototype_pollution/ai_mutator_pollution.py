import json
import random

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload_dict = {
            "__proto__": {
                "polluted": "CRITICAL_POLLUTION_HIT",
                "isAdmin": True
            }
        }
    else:
        payload_dict = {
            "user": {
                "name": "guest_" + str(random.randint(100, 999)),
                "role": "visitor"
            }
        }

    raw = json.dumps(payload_dict).encode("utf-8")
    return bytearray(raw[:max_size])

def deinit():
    pass
