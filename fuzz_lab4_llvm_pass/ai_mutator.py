import socket
import os
import struct

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
    # 1. Coba ambil smart seed dari LLM Daemon
    if client_sock:
        try:
            client_sock.sendall(b"REQ\n")
            data = client_sock.recv(4096)
            if data and data != b"EMPTY":
                return bytearray(data[:max_size])
        except Exception:
            pass

    # 2. Fallback Cerdas: Jaga header tetap valid, perbesar payload (Heap Overflow Trigger)
    mutated = bytearray(buf)
    if len(mutated) >= 9:
        # Pertahankan "PACK\x02", set chunk_count = 1 (16 byte), perbesar payload_len = 64 byte
        header = struct.pack("<4sBHH", b"PACK", 0x02, 1, 64)
        payload = b"\x7f\x45" + (b"A" * 62)
        return bytearray(header + payload)
    
    return mutated

def deinit():
    global client_sock
    if client_sock:
        try:
            client_sock.close()
        except Exception:
            pass
