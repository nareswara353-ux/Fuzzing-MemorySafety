import socket
import os
import struct

SOCKET_PATH = "/tmp/llm_fuzz_bridge.sock"
client_sock = None

def init(seed):
    global client_sock
    try:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(SOCKET_PATH)
    except Exception:
        client_sock = None

def fuzz(buf, add_buf, max_size):
    global client_sock
    if client_sock:
        try:
            client_sock.sendall(b"REQ_SEED\n")
            data = client_sock.recv(4096)
            if data and data != b"EMPTY":
                return bytearray(data[:max_size])
        except Exception:
            pass

    mutated = bytearray(buf)
    if len(mutated) > 0:
        mutated[0] = (mutated[0] + 1) & 0xFF
    return mutated

def deinit():
    global client_sock
    if client_sock:
        try:
            client_sock.close()
        except Exception:
            pass
