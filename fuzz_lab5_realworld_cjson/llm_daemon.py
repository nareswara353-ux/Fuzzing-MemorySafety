import socket
import os
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
    if not os.path.exists(CONSTRAINTS_FILE):
        return [], []
    with open(CONSTRAINTS_FILE, "r") as f:
        data = json.load(f)
        return data.get("extracted_integers", []), data.get("hex_tokens", [])

extracted_ints, extracted_hex = load_compiler_constraints()
print(f"[+] Loaded cJSON Compiler Feedback: {len(extracted_ints)} ints, {len(extracted_hex)} tokens")

DYNAMIC_PROMPT = f"""You are a specialized JSON parser fuzzing engine.
Compiler analysis revealed token constraints: {extracted_hex[:10]}
Task: Generate an edge-case JSON payload to test parser robustness.
Try techniques like:
- Deeply nested objects or arrays: {{"a": {{"b": ...}}}}
- Boundary numbers: 1e308, -1e-308, 99999999999999999999
- Malformed unicode escapes or long keys
- Mixed null/bool/float structures

Output ONLY raw JSON string (no markdown, no backticks, no commentary).
"""

def query_ollama_for_seed():
    payload = {
        "model": MODEL_NAME,
        "prompt": DYNAMIC_PROMPT,
        "stream": False
    }
    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data.get("response", "").strip()
            # Bersihkan jika LLM membungkus kode dalam markdown block
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
            return text.encode('utf-8')
    except Exception:
        return None

def llm_worker():
    print(f"[+] LLM JSON Mutator Producer Active ({MODEL_NAME})")
    while True:
        if len(seed_pool) < 10:
            seed = query_ollama_for_seed()
            if seed:
                with pool_lock:
                    seed_pool.append(seed)
                print(f"[+] [cJSON Mutator] Generated edge-case JSON ({len(seed)} B) | Pool: {len(seed_pool)}")
            else:
                time.sleep(0.5)
        else:
            time.sleep(0.3)

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

print(f"[*] IPC Daemon listening on {SOCKET_PATH}...")
while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
