import socket
import os
import struct
import json
import urllib.request
import threading
import time

SOCKET_PATH = "/tmp/llm_adaptive_bridge.sock"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
CONSTRAINTS_FILE = "extracted_constraints.json"

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)

seed_pool = []
pool_lock = threading.Lock()
burst_requested = threading.Event()

def load_compiler_constraints():
    if not os.path.exists(CONSTRAINTS_FILE):
        return [], []
    with open(CONSTRAINTS_FILE, "r") as f:
        data = json.load(f)
        return data.get("extracted_integers", []), data.get("hex_tokens", [])

extracted_ints, extracted_hex = load_compiler_constraints()
print(f"[+] [Adaptive Daemon] Compiler Constraints: {len(extracted_ints)} ints, {len(extracted_hex)} tokens")

PROMPT = f"""You are an adaptive fuzzing solver breaking a coverage plateau.
Target Bitcode Invariants:
- Magic/Hex: {extracted_hex}
- Bounds: {extracted_ints}

Generate a boundary-breaking binary payload (Heap Overflow Candidate):
1. "chunk_count": 1
2. "payload_hex": Hex starting with "7f45" followed by 64+ hex characters.

Output ONLY JSON:
{{"chunk_count": 1, "payload_hex": "7f45414141414141414141414141414141414141414141414141414141414141414141414141"}}
"""

def generate_seed():
    payload = {"model": MODEL_NAME, "prompt": PROMPT, "stream": False, "format": "json"}
    try:
        req = urllib.request.Request(OLLAMA_API_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res = json.loads(data.get("response", "{}"))
            chunk = int(res.get("chunk_count", 1))
            p_hex = res.get("payload_hex", "7f45" + "41" * 32).strip()
            p_bytes = bytes.fromhex(p_hex)
            header = struct.pack("<4sBHH", b"PACK", 0x02, chunk, len(p_bytes))
            return header + p_bytes
    except Exception:
        return None

def producer_thread():
    print("[+] Adaptive Producer Thread Ready.")
    while True:
        # Hanya generate saat pool menipis
        with pool_lock:
            pool_len = len(seed_pool)
        
        if pool_len < 10:
            seed = generate_seed()
            if seed:
                with pool_lock:
                    seed_pool.append(seed)
                print(f"[+] [Plateau Breaker] Stored Seed in Pool (Total: {len(seed_pool)})")
        else:
            time.sleep(0.3)

threading.Thread(target=producer_thread, daemon=True).start()

def handle_client(conn):
    while True:
        try:
            req = conn.recv(1024)
            if not req:
                break
            payload = None
            if b"REQ_BURST" in req:
                with pool_lock:
                    if seed_pool:
                        payload = seed_pool.pop(0)
            conn.sendall(payload if payload else b"EMPTY")
        except Exception:
            break
    conn.close()

print(f"[*] Adaptive Socket listening on {SOCKET_PATH}...")
while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
