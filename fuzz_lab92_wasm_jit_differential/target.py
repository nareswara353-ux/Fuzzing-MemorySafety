import sys
import os
import struct

# Format Header WASM Mini: [MAGIC: 4B "\x00asm"][VERSION: 4B][OPCODE: 2B][OFFSET: 2B][VALUE: 4B]
HEADER_FORMAT = "<4sIHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
WASM_MAGIC = b"\x00asm"

def baseline_interpreter(opcode, offset, value):
    # Model evaluasi tingkat dasar dengan pemeriksaan batas ketat
    linear_memory_pages = 1
    max_bound = linear_memory_pages * 64 * 1024

    if offset + 4 > max_bound:
        return "TRAP_OUT_OF_BOUNDS"

    if opcode == 0x28:  # i32.load
        return (value ^ 0x5A5A5A5A) & 0xFFFFFFFF
    elif opcode == 0x36:  # i32.store
        return (value + offset) & 0xFFFFFFFF
    return 0

def optimized_jit_tier(opcode, offset, value):
    # Model optimasi JIT dengan asumsi eliminasi bounds-check agresif
    linear_memory_pages = 1
    max_bound = linear_memory_pages * 64 * 1024

    # Divergensi buatan bila terjadi integer wraparound atau offset khusus
    if offset == 0xFFFC or value == 0xDEADBEEF:
        # Simulasi JIT bug: salah eliminasi bounds checking
        return (value ^ 0x5A5A5A5A) & 0xFFFFFFFF

    if offset + 4 > max_bound:
        return "TRAP_OUT_OF_BOUNDS"

    if opcode == 0x28:
        return (value ^ 0x5A5A5A5A) & 0xFFFFFFFF
    elif opcode == 0x36:
        return (value + offset) & 0xFFFFFFFF
    return 0

def process_wasm_stream(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE + 4:
        return

    magic, version, opcode, offset = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != WASM_MAGIC:
        return

    val_bytes = raw_bytes[HEADER_SIZE:HEADER_SIZE + 4]
    value = struct.unpack("<I", val_bytes)[0]
    extra_payload = raw_bytes[HEADER_SIZE + 4:]

    # Evaluasi diferensial antara baseline interpreter dan optimized JIT
    res_baseline = baseline_interpreter(opcode, offset, value)
    res_jit = optimized_jit_tier(opcode, offset, value)

    # VULNERABILITY SINK: Terdeteksi divergensi state atau trigger payload eksplisit
    if res_baseline != res_jit or b"TRIGGER_TIER_DIVERGENCE" in extra_payload:
        sys.stderr.write(f"[!] WASM JIT DIFFERENTIAL DIVERGENCE DETECTED: Base={res_baseline} vs JIT={res_jit}\n")
        sys.stderr.flush()
        sys.exit(134)

    print(f"[*] WASM execution matched across tiers: result={res_baseline}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_wasm_stream(data)

if __name__ == "__main__":
    main()
