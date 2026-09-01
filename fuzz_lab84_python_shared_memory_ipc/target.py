import sys
import os
import struct
from multiprocessing import shared_memory

# Header Format: [MAGIC: 4B "SHM\x00"][OFFSET: 2B][LENGTH: 2B][DATA: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SHM_CAPACITY = 64

def process_shared_memory(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, offset, length = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"SHM\x00":
        return

    data = raw_bytes[HEADER_SIZE:]

    # Buat segment shared memory sementara
    shm_name = f"fuzz_shm_{os.getpid()}"
    try:
        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=SHM_CAPACITY)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=shm_name)

    try:
        buf = shm.buf
        
        # VULNERABILITY SINK: Penulisan di luar batas kapasitas shared memory
        if offset + length > SHM_CAPACITY or b"TRIGGER_SHM_OOB" in data:
            sys.stderr.write("[!] PYTHON SHARED MEMORY IPC BOUNDARY SINK HIT\n")
            sys.stderr.flush()
            sys.exit(134)

        if len(data) >= length:
            buf[offset:offset + length] = data[:length]
            print(f"[*] Shared memory write completed safely: offset={offset}, len={length}")
    finally:
        shm.close()
        shm.unlink()

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_shared_memory(data)

if __name__ == "__main__":
    main()
