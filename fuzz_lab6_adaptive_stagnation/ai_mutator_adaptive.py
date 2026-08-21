import socket
import os
import struct
import time

SOCKET_PATH = "/tmp/llm_adaptive_bridge.sock"
client_sock = None

# Telemetri & State Stagnasi
exec_count = 0
last_interesting_exec = 0
STAGNATION_THRESHOLD = 500  # Pemicu burst LLM jika 500 eksekusi tanpa edge baru
burst_mode = False
burst_budget = 0

def init(seed):
    global client_sock
    try:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(SOCKET_PATH)
        client_sock.settimeout(0.05)
    except Exception:
        client_sock = None

def fuzz(buf, add_buf, max_size):
    global client_sock, exec_count, last_interesting_exec, burst_mode, burst_budget
    exec_count += 1

    # Cek apakah mengalami stagnasi
    if not burst_mode and (exec_count - last_interesting_exec > STAGNATION_THRESHOLD):
        burst_mode = True
        burst_budget = 10  # Minta 10 smart seed berturut-turut dari LLM

    # Mode 1: AI Burst Mode (Ketika Stagnan)
    if burst_mode and client_sock and burst_budget > 0:
        burst_budget -= 1
        try:
            client_sock.sendall(b"REQ_BURST\n")
            data = client_sock.recv(4096)
            if data and data != b"EMPTY":
                if burst_budget == 0:
                    burst_mode = False
                    last_interesting_exec = exec_count  # Reset counter
                return bytearray(data[:max_size])
        except Exception:
            burst_mode = False

    # Mode 2: Ultra-Fast In-Memory Mutation (Non-Stagnant / Havoc Cepat)
    mutated = bytearray(buf)
    if len(mutated) >= 9:
        # Mutasi bit/byte cepat tanpa jeda socket
        idx = (exec_count % (len(mutated) - 8)) + 8
        mutated[idx] = (mutated[idx] + 1) & 0xFF
        return mutated

    return mutated

def deinit():
    global client_sock
    if client_sock:
        try:
            client_sock.close()
        except Exception:
            pass
