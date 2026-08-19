import socket
import os
import json
import time
import threading

SOCKET_PATH = "/tmp/llm_bridge.sock"

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)

print(f"[*] LLM Daemon listening on {SOCKET_PATH}...")

# Pool seed hasil generasi LLM yang siap diambil AFL++
seed_pool = [
    b"PACK\x02\x01\x00\x40\x00" + b"A" * 64,
    b"PACK\x02\x02\x00\x80\x00" + b"\x7FE" + b"B" * 126
]

def handle_client(conn):
    while True:
        try:
            req = conn.recv(1024)
            if not req:
                break
            
            # Berikan seed mutasi dari antrean secara instan (non-blocking untuk AFL++)
            if seed_pool:
                reply = seed_pool.pop(0)
                conn.sendall(reply)
            else:
                conn.sendall(b"EMPTY")
        except Exception:
            break
    conn.close()

while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()