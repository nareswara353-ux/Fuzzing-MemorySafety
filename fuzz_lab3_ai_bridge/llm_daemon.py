import socket
import os
import struct
import json
import urllib.request
import threading
import time

SOCKET_PATH = "/tmp/llm_bridge.sock"
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

def load_compiler_constraints():
    """Muat metadata konstanta hasil ekstraksi LLVM Pass."""
    if not os.path.exists(CONSTRAINTS_FILE):
        return [], []
    with open(CONSTRAINTS_FILE, "r") as f:
        data = json.load(f)
        return data.get("extracted_integers", []), data.get("hex_tokens", [])

extracted_ints, extracted_hex = load_compiler_constraints()
print(f"[+] Loaded Compiler Feedback: {len(extracted_ints)} integers, {len(extracted_hex)} hex tokens")

# Konstruksi prompt dinamis berbasis hasil analisis LLVM Pass
DYNAMIC_PROMPT = f"""You are an automated fuzzing mutation engine guided by compiler analysis.
Target binary constraints extracted via LLVM Pass:
- Magic/Hex tokens found in IR: {extracted_hex}
- Critical integer bounds/branches: {extracted_ints}

Generate a binary payload matching these rules:
1. "magic": "PACK"
2. "version": 2
3. "chunk_count": Pick an integer <= 16 from the bounds.
4. "payload_hex": Hex string of bytes to copy. To trigger heap overflow, payload length MUST be strictly greater than (chunk_count * 16). Inject hex tokens {extracted_hex} at the start of payload.

Output ONLY a JSON object:
{{"chunk_count": 1, "payload_hex": "7f4541414141414141414141414141414141414141414141414141414141414141"}}
"""

def query_ollama_for_seed():
    payload = {
        "model": MODEL_NAME,
        "prompt": DYNAMIC_PROMPT,
        "stream": False,
        "format": "json"
    }
    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res = json.loads(data.get("response", "{}"))
            
            chunk_count = int(res.get("chunk_count", 1))
            payload_hex = res.get("payload_hex", "7f45" + "41" * 32)
            payload_bytes = bytes.fromhex(payload_hex.strip())
            
            header = struct.pack("<4sBHH", b"PACK", 0x02, chunk_count, len(payload_bytes))
            return header + payload_bytes
    except Exception as e:
        return None

def llm_worker():
    print(f"[+] LLM Producer Active with model: {MODEL_NAME}")
    while True:
        if len(seed_pool) < 15:
            seed = query_ollama_for_seed()
            if seed:
                with pool_lock:
                    seed_pool.append(seed)
                print(f"[+] [Closed-Loop] Synthesized seed ({len(seed)} bytes) | Queue: {len(seed_pool)}")
            else:
                time.sleep(0.5)
        else:
            time.sleep(0.2)

threading.Thread(target=llm_worker, daemon=True).start()

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
            conn.sendall(payload if payload else b"EMPTY")
        except Exception:
            break
    conn.close()

print(f"[*] Closed-Loop IPC Daemon listening on {SOCKET_PATH}...")
while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()