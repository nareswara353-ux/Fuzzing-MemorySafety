import random

SAFE_HTTP_TEMPLATE = (
    b"POST /api/v1/data HTTP/1.1\r\n"
    b"Host: internal.service\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 18\r\n"
    b"\r\n"
    b'{"status":"valid"}'
)

SMUGGLED_HTTP_TEMPLATE = (
    b"POST / HTTP/1.1\r\n"
    b"Host: internal.service\r\n"
    b"Content-Length: 6\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"\r\n"
    b"0\r\n"
    b"\r\n"
    b"POST /admin/update HTTP/1.1\r\n"
    b"Host: internal.service\r\n"
    b"X-Payload: SMUGGLED_ADMIN_ACTION\r\n"
    b"\r\n"
)

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = SMUGGLED_HTTP_TEMPLATE
    else:
        payload = SAFE_HTTP_TEMPLATE

    return bytearray(payload[:max_size])

def deinit():
    pass
