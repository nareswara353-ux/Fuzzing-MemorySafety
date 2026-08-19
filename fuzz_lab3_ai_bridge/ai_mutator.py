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
        client_sock.settimeout(0.005)
    except Exception:
        client_sock = None

def fuzz_count(buf):
    return 8

def fuzz(buf, add_buf, max_size):
    global client_sock
    
    # Prioritas 1: Ambil seed baru dari LLM Daemon via Socket
    if client_sock:
        try:
            client_sock.sendall(b"GET_MUTATION")
            data = client_sock.recv(4096)
            if data and data != b"EMPTY":
                return bytearray(data[:max_size])
        except Exception:
            pass

    # Prioritas 2: Fallback Invariant-Preserving Mutation
    mutated = bytearray(buf)
    if len(mutated) < 9:
        mutated = bytearray(b"PACK\x02\x01\x00\x10\x00" + b"B" * 16)
    else:
        # Paksa integritas header
        mutated[0:4] = b"PACK"
        mutated[4] = 0x02
        mutated[5:7] = struct.pack("<H", 1)   # Alloc 16 bytes
        mutated[7:9] = struct.pack("<H", 64)  # Payload 64 bytes
        if len(mutated) < 73:
            mutated.extend(b"C" * (73 - len(mutated)))

    return mutated[:max_size]

def deinit():
    global client_sock
    if client_sock:
        client_sock.close()