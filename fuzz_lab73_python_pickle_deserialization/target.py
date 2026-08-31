import sys
import os
import struct

def deserialize_stream(raw_bytes):
    # Header format: [MAGIC: 4 Bytes "PKL\x00"][OPCODE: 1 Byte][PAYLOAD: N Bytes]
    if len(raw_bytes) < 5:
        return

    magic, opcode = struct.unpack("<4sB", raw_bytes[:5])
    if magic != b"PKL\x00":
        return

    payload = raw_bytes[5:]

    # Deteksi Opcode berbahaya (0xFE = DYNAMIC_CALLABLE_REDUCE) atau injeksi token eksekusi
    if opcode == 0xFE or b"CRITICAL_PICKLE_EXEC" in payload:
        sys.stderr.write("[!] INSECURE DESERIALIZATION OPCODE SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)
    elif opcode == 0x01:
        # Safe Integer Deserialization
        if len(payload) >= 4:
            _ = struct.unpack("<I", payload[:4])[0]
    elif opcode == 0x02:
        # Safe String Deserialization
        _ = payload.decode(errors="ignore")

    print("[*] Object stream deserialized safely")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    try:
        deserialize_stream(data)
    except Exception as e:
        print(f"Captured error: {e}")

if __name__ == "__main__":
    main()
