import base64
import json
import random

def b64url(data_bytes):
    return base64.urlsafe_b64encode(data_bytes).rstrip(b"=").decode("utf-8")

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        header = {"typ": "JWT", "alg": "none"}
        payload = {"user": "hacker", "role": "admin", "admin": True}
        sig = ""
    else:
        header = {"typ": "JWT", "alg": "HS256"}
        payload = {"user": "guest", "role": "user"}
        sig = b64url(b"invalidsignature123")

    h_str = b64url(json.dumps(header).encode("utf-8"))
    p_str = b64url(json.dumps(payload).encode("utf-8"))

    jwt_token = f"{h_str}.{p_str}.{sig}"
    return bytearray(jwt_token.encode("utf-8")[:max_size])

def deinit():
    pass
