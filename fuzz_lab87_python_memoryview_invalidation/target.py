import sys
import os
import struct

# Format Header: [MAGIC: 4B "MVW\x00"][ACTION_FLAG: 2B][OFFSET: 2B][DATA: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
BUFFER_POOL_SIZE = 64

def process_memoryview_stream(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, action_flag, offset = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"MVW\x00":
        return

    payload = raw_bytes[HEADER_SIZE:]

    # Backing storage buffer
    backing_buffer = bytearray(b"X" * BUFFER_POOL_SIZE)
    mv = memoryview(backing_buffer)

    # VULNERABILITY SINK: Mengakses view pasca invalidasi atau mutasi liar
    if action_flag == 0xDEAD or b"TRIGGER_BUFFER_INVALIDATION" in payload or offset > 100:
        mv.release()
        sys.stderr.write("[!] PYTHON MEMORYVIEW BUFFER INVALIDATION SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    # Valid execution: safe sub-slicing
    try:
        safe_offset = offset % BUFFER_POOL_SIZE
        sub_view = mv[safe_offset:BUFFER_POOL_SIZE]
        _ = sub_view.tobytes()
        mv.release()
        print(f"[*] Memoryview slice operated safely at offset={safe_offset}")
    except (BufferError, IndexError, ValueError):
        pass

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_memoryview_stream(data)

if __name__ == "__main__":
    main()
