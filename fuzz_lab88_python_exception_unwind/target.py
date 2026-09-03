import sys
import os
import struct

# Format Header: [MAGIC: 4B "EXC\x00"][DEPTH: 2B][FLAGS: 2B][PAYLOAD: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def recursive_unwind_frame(current_depth, max_depth, trigger_fault):
    if current_depth >= max_depth:
        if trigger_fault:
            raise RuntimeError("TRIGGER_UNWIND_FAULT")
        return "SAFE_DEPTH_REACHED"

    try:
        return recursive_unwind_frame(current_depth + 1, max_depth, trigger_fault)
    except RuntimeError as e:
        # Simulasi deteksi korupsi frame saat proses unwinding mencapai root
        if current_depth == 0 and trigger_fault:
            sys.stderr.write("[!] PYTHON EXCEPTION UNWINDING CORRUPTION SINK HIT\n")
            sys.stderr.flush()
            sys.exit(134)
        raise e

def process_unwind_stream(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, depth, flags = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"EXC\x00":
        return

    payload = raw_bytes[HEADER_SIZE:]
    trigger_fault = (flags == 0xDEAD) or (b"TRIGGER_UNWIND_PANIC" in payload) or (depth > 200)

    try:
        res = recursive_unwind_frame(0, min(depth, 50), trigger_fault)
        print(f"[*] Call stack safely unwound: result={res}")
    except RuntimeError:
        pass

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_unwind_stream(data)

if __name__ == "__main__":
    main()
