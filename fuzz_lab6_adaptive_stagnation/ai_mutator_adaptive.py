import socket
import os
import struct
import random

SOCKET_PATH = "/tmp/llm_adaptive_bridge.sock"
client_sock = None

exec_count = 0
last_burst_exec = 0
STAGNATION_THRESHOLD = 300  # Pemicu burst tiap 300 eksekusi

def init(seed):
    global client_sock
    try:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(SOCKET_PATH)
        client_sock.settimeout(0.05)
    except Exception:
        client_sock = None

def fuzz(buf, add_buf, max_size):
    global client_sock, exec_count, last_burst_exec
    exec_count += 1

    # Cek apakah sudah waktunya burst LLM
    if exec_count - last_burst_exec > STAGNATION_THRESHOLD:
        last_burst_exec = exec_count
        
        # 1. Coba ambil smart seed dari LLM Daemon
        if client_sock:
            try:
                client_sock.sendall(b"REQ_BURST\n")
                data = client_sock.recv(4096)
                if data and data != b"EMPTY":
                    return bytearray(data[:max_size])
            except Exception:
                pass

        # 2. Smart Fallback Burst: Paksa trigger boundary constraint (chunk=1, len=64)
        header = struct.pack("<4sBHH", b"PACK", 0x02, 1, 64)
        payload = b"\x7f\x45" + (b"A" * 62)
        return bytearray(header + payload)

    # 3. Ultra-Fast Mutation: Modifikasi byte payload biasa
    mutated = bytearray(buf)
    if len(mutated) > 9:
        pos = random.randint(9, len(mutated) - 1)
        mutated[pos] = (mutated[pos] + 1) & 0xFF
    return mutated

def deinit():
    global client_sock
    if client_sock:
        try:
            client_sock.close()
        except Exception:
            pass
