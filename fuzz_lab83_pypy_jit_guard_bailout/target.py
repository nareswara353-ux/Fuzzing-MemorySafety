import sys
import os
import struct

# Format Payload: [MAGIC: 4B "JIT\x00"][LOOP_ITERS: 2B][GUARD_TYPE: 2B][PAYLOAD: 32B]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def execute_traced_loop(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, loop_iters, guard_type = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"JIT\x00":
        return

    payload_data = raw_bytes[HEADER_SIZE:]

    # Simulasi status JIT tracing optimizer
    jit_compiled = False
    accumulator = 0

    for i in range(min(loop_iters, 1000)):
        if i == 50:
            jit_compiled = True  # Trace terkompilasi menjadi hot loop

        # Evaluasi Guard: Guard memverifikasi tipe integer murni
        if jit_compiled and (guard_type == 0xDEAD or b"TRIGGER_GUARD_FAIL" in payload_data):
            # VULNERABILITY SINK: JIT Bailout Deopt State Desync
            sys.stderr.write("[!] PYPY JIT TRACE GUARD FAILURE DEOPT SINK HIT\n")
            sys.stderr.flush()
            sys.exit(134)

        accumulator += (i & 0xFF)

    print(f"[*] Traced loop completed safely: iters={loop_iters}, acc={accumulator}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    execute_traced_loop(data)

if __name__ == "__main__":
    main()
