import sys
import os
import gc
import struct

# Format Header: [MAGIC: 4B "GCC\x00"][GEN_TARGET: 2B][FLAGS: 2B][DATA: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

retained_container = []

class CyclicMember:
    def __init__(self, item_id, trigger_retention):
        self.item_id = item_id
        self.trigger_retention = trigger_retention
        self.peer = None

    def __del__(self):
        if self.trigger_retention:
            # Re-referencing objek kembali ke live scope saat finalizer dipanggil
            retained_container.append(self)
            sys.stderr.write("[!] PYTHON GC CYCLIC RETENTION SINK HIT\n")
            sys.stderr.flush()
            sys.exit(134)

def process_gc_cycles(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, gen_target, flags = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"GCC\x00":
        return

    payload = raw_bytes[HEADER_SIZE:]
    trigger_retention = (flags == 0xDEAD) or (b"TRIGGER_GC_SINK" in payload) or (gen_target > 5)

    # Membentuk cyclic graph antar dua instance
    node_a = CyclicMember(1001, trigger_retention)
    node_b = CyclicMember(1002, False)
    node_a.peer = node_b
    node_b.peer = node_a

    # Hapus referensi lokal di stack frame agar siklus menjadi unreachable
    del node_a
    del node_b

    # Eksekusi eksplisit siklus sweep GC
    sweep_generation = min(gen_target, 2)
    gc.collect(sweep_generation)
    print(f"[*] GC sweep completed safely for generation={sweep_generation}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_gc_cycles(data)

if __name__ == "__main__":
    main()
