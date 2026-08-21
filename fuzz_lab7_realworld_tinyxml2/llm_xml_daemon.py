import socket
import os
import json
import urllib.request
import threading
import time

SOCKET_PATH = "/tmp/llm_xml_bridge.sock"
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
print(f"[+] [XML Daemon] Loaded {len(extracted_hex)} tokens from TinyXML-2 LLVM bitcode")

PROMPT = """You are an XML grammar fuzzer. Generate a highly complex, edge-case XML payload.
Techniques to use:
- Deeply nested tags: <a1><a2><a3>...</a3></a2></a1>
- Complex attributes, namespaces, and CDATA sections: <root attr="val"><![CDATA[...]]></root>
- Special entities, malformed closing tags, long element names.

Output ONLY the raw XML string without any markdown formatting or commentary.
"""

def query_llm():
    payload = {"model": MODEL_NAME, "prompt": PROMPT, "stream": False}
    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data.get("response", "").strip()
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
            return text.encode('utf-8')
    except Exception:
        return None

def producer_worker():
    print(f"[+] XML Neural Producer active ({MODEL_NAME})")
    while True:
        with pool_lock:
            count = len(seed_pool)
        if count < 10:
            seed = query_llm()
            if seed:
                with pool_lock:
                    seed_pool.append(seed)
                print(f"[+] [XML Mutator] Enqueued seed ({len(seed)} B) | Pool: {len(seed_pool)}")
            else:
                time.sleep(0.5)
        else:
            time.sleep(0.3)

threading.Thread(target=producer_worker, daemon=True).start()

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

print(f"[*] XML Socket listening on {SOCKET_PATH}...")
while True:
    conn, _ = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
