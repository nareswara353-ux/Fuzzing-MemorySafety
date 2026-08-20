import socket
import os
import struct
import random
import time
import threading

SOCKET_PATH = "/tmp/llm_bridge.sock"

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)

seed_pool = []
pool_lock = threading.Lock()

def llm_synthesis_worker():
    """
    Background Worker: Mensimulasikan/memanggil generator LLM 
    untuk memproduksi batch variasi biner terstruktur secara kontinu.
    """
    print("[+] Background LLM Generator Worker started.")
    while True:
        if len(seed_pool) < 20:
            batch = []
            for _ in range(10):
                magic = b"PACK"
                version = 0x02
                
                if random.random() < 0.4:
                    chunks = random.randint(1, 2)
                    p_len = (chunks * 16) + random.randint(16, 200)
                    body = b"\x7FE" + b"A" * (p_len - 2)
                else:
                    chunks = random.randint(1, 8)
                    p_len = chunks * 16
                    body = os.urandom(p_len)

                header = struct.pack("<4sBHH", magic, version, chunks, p_len)
                batch.append(header + body)

            with pool_lock:
                seed_pool.extend(batch)

        time.sleep(0.05) 
        
threading.Thread(target=llm_synthesis_worker, daemon=True).start()

def handle_client(conn):
    while True:
        try:
            req = conn.recv(1024)
            if not req:
                break
            
            payload = None
            with pool_lock:
                if seed_pool:
                    payload = seed_pool.pop(0)

            if payload:
                conn.sendall(payload)
            else:
                conn.sendall(b"EMPTY")
        except Exception:
            break
    conn.close()

print(f"[*] LLM Daemon listening on {SOCKET_PATH}...")
while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()