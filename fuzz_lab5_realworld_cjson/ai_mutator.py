import socket
import os
import random

SOCKET_PATH = "/tmp/llm_bridge.sock"
client_sock = None

def init(seed):
    global client_sock
    try:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(SOCKET_PATH)
        client_sock.settimeout(0.05)
    except Exception:
        client_sock = None

def fuzz(buf, add_buf, max_size):
    global client_sock
    # 1. Coba ambil smart structured seed dari LLM
    if client_sock:
        try:
            client_sock.sendall(b"REQ\n")
            data = client_sock.recv(65536)
            if data and data != b"EMPTY":
                return bytearray(data[:max_size])
        except Exception:
            pass

    # 2. Fast Mutation Fallback (JSON character swaps/insertions)
    mutated = bytearray(buf)
    if len(mutated) > 0:
        pos = random.randint(0, len(mutated) - 1)
        tokens = [b"{", b"}", b"[", b"]", b":", b",", b"\"", b"\\", b"\x00"]
        mutated[pos] = random.choice(tokens)[0]
    return mutated

def deinit():
    global client_sock
    if client_sock:
        try:
            client_sock.close()
        except Exception:
            pass
