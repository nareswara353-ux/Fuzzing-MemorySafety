import urllib.request
import json
import struct
import os

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")

os.makedirs("in", exist_ok=True)

PROMPT = """Generate a JSON object for a binary fuzzer testcase:
{
  "chunk_count": 1,
  "payload_hex": "7f45414141414141414141414141414141414141414141414141414141414141"
}
Rules:
- "chunk_count": integer between 1 and 4
- "payload_hex": hex string starting with "7f45" followed by 30 to 80 hex chars.
Output ONLY valid JSON.
"""

print(f"[*] Pre-generating 5 smart AI seeds using {MODEL_NAME}...")

for i in range(5):
    payload = {"model": MODEL_NAME, "prompt": PROMPT, "stream": False, "format": "json"}
    try:
        req = urllib.request.Request(OLLAMA_API_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res = json.loads(data.get("response", "{}"))
            
            chunk_count = int(res.get("chunk_count", 1))
            payload_hex = res.get("payload_hex", "7f45" + "41" * 32)
            payload_bytes = bytes.fromhex(payload_hex.strip())
            
            header = struct.pack("<4sBHH", b"PACK", 0x02, chunk_count, len(payload_bytes))
            seed_data = header + payload_bytes
            
            filename = f"in/seed_ai_{i}.bin"
            with open(filename, "wb") as f:
                f.write(seed_data)
            print(f"  [+] Created {filename} ({len(seed_data)} bytes)")
    except Exception as e:
        print(f"  [-] Error generating seed {i}: {e}")

print("[+] Done seeding corpus.")
