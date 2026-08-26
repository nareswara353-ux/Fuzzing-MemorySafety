import random
import struct

CLUSTER_MAGIC = 0x54534944 # 'DIST'

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    magic = CLUSTER_MAGIC
    node_id = random.randint(1, 16)
    seq_id = random.randint(100, 9999)
    cmd = random.choice([0x01, 0x02, 0xCC])

    if random.random() < 0.6:
        # Injeksi payload pemicu sink
        payload = b"CLUSTER_SYNC_ALL" + bytearray(random.getrandbits(8) for _ in range(16))
    else:
        payload = bytearray(random.getrandbits(8) for _ in range(24))

    payload_len = min(len(payload), 64)
    padded_payload = bytes(payload).ljust(64, b"\x00")[:64]

    raw = struct.pack("<IHHBB64s", magic, node_id, seq_id, cmd, payload_len, padded_payload)
    return bytearray(raw[:max_size])

def deinit():
    pass
