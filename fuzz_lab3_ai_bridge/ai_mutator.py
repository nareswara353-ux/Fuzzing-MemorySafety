import socket
import os

SOCKET_PATH = "/tmp/llm_bridge.sock"
client_sock = None

def init(seed):
    global client_sock
    try:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(SOCKET_PATH)
        client_sock.settimeout(0.002)  # Non-blocking 2ms timeout
    except Exception:
        client_sock = None

def fuzz_count(buf):
    return 4

def fuzz(buf, add_buf, max_size):
    global client_sock
    if client_sock:
        try:
            client_sock.sendall(b"GET_MUTATION")
            data = client_sock.recv(4096)
            if data and data != b"EMPTY":
                return bytearray(data[:max_size])
        except Exception:
            pass

    # Fallback mutation jika socket kosong/timeout
    mutated = bytearray(buf)
    if len(mutated) >= 9:
        mutated[5:7] = b"\x01\x00"
        mutated[7:9] = b"\x80\x00"  # 128 bytes
        mutated.extend(b"\x41" * 128)
    return mutated[:max_size]

def deinit():
    global client_sock
    if client_sock:
        client_sock.close()