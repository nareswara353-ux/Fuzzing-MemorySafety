import random
import struct

MSG_HELLO = 0x01
MSG_AUTH  = 0x02
MSG_DATA  = 0x03
MSG_QUIT  = 0x04

def init(seed):
    random.seed(seed)

def build_message(msg_type, payload):
    return struct.pack("<BB", msg_type, len(payload)) + payload

def fuzz(buf, add_buf, max_size):
    # Step 1: Kunci sekuens wajib untuk mencapai State AUTHENTICATED
    msg_hello = build_message(MSG_HELLO, b"HELO")
    msg_auth = build_message(MSG_AUTH, struct.pack("<I", 0x1337C0DE))

    # Step 2: Mutasi pada pesan DATA berikutnya
    if random.random() < 0.6:
        data_payload = bytearray(random.getrandbits(8) for _ in range(32))
    else:
        data_payload = bytearray(b"A" * random.randint(4, 16))

    msg_data = build_message(MSG_DATA, bytes(data_payload))
    msg_quit = build_message(MSG_QUIT, b"")

    stream = msg_hello + msg_auth + msg_data + msg_quit
    return bytearray(stream[:max_size])

def deinit():
    pass
