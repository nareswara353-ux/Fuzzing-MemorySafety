import os
import sys
import random
import struct
import json
import urllib.request

class LLMMutator:
    def __init__(self):
        # Konfigurasi endpoint LLM lokal (Ollama / Local OpenAI Compatible Server)
        self.api_url = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
        self.model_name = os.getenv("LLM_MODEL", "llama3")
        self.call_counter = 0
        self.llm_frequency = 20  # Panggil LLM sekali setiap 20 iterasi custom fuzz

    def query_local_llm(self, prompt: str) -> str:
        """Kirim prompt ke local LLM inference server via HTTP request."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result.get("response", "")
        except Exception:
            # Fallback jika backend LLM belum aktif atau timeout
            return ""

    def semantic_reconstruction(self, buf: bytearray) -> bytearray:
        """
        Structure-aware mutation yang merekonstruksi Header PACK
        berdasarkan pemahaman semantik grammar parser.
        """
        if len(buf) < 9:
            # Seed terlalu pendek, rekonstruksi header standar
            return bytearray(b"PACK\x02\x01\x00\x10\x00" + b"A" * 16)

        # Parsing field eksisting
        magic = buf[0:4]
        version = buf[4]
        chunk_count = struct.unpack("<H", buf[5:7])[0]
        payload_len = struct.unpack("<H", buf[7:9])[0]

        strategy = random.randint(0, 3)

        if strategy == 0:
            # Perbaiki magic & version secara deterministik
            buf[0:4] = b"PACK"
            buf[4] = 0x02

        elif strategy == 1:
            # Mutasi Relasional: payload_len dibuat melebihi chunk_count * 16
            mutated_chunk = random.randint(1, 4)
            mutated_len = (mutated_chunk * 16) + random.randint(1, 128)
            buf[5:7] = struct.pack("<H", mutated_chunk)
            buf[7:9] = struct.pack("<H", mutated_len)

            # Sesuaikan ukuran body data agar lolos gate file size
            current_body_len = len(buf) - 9
            if current_body_len < mutated_len:
                buf.extend(b"\x41" * (mutated_len - current_body_len))

        elif strategy == 2:
            # Mutasi State Payload khusus (Trigger branch dynamic_buf[0] == 0x7F && dynamic_buf[1] == 'E')
            if len(buf) > 10:
                buf[9] = 0x7F
                buf[10] = ord('E')

        return buf


# --- AFL++ Custom Mutator API Interface Callbacks ---

mutator_instance = None

def init(seed):
    global mutator_instance
    mutator_instance = LLMMutator()
    print("[+] [AFL++ Python Mutator] Initialized successfully.", file=sys.stderr)

def fuzz_count(buf):
    # Tentukan berapa kali fungsi fuzz() dipanggil per queue item
    return 4

def fuzz(buf, add_buf, max_size):
    global mutator_instance
    mutated = bytearray(buf)
    
    mutator_instance.call_counter += 1

    # Eksekusi hybrid mutation
    mutated = mutator_instance.semantic_reconstruction(mutated)

    if len(mutated) > max_size:
        mutated = mutated[:max_size]

    return mutated

def deinit():
    print("[*] [AFL++ Python Mutator] Deinitialized.", file=sys.stderr)