import sys
import os
import struct
import dis

# Header format: [MAGIC: 4B "BCF\x00"][OPCODE_COUNT: 2B][RESERVED: 2B][OPCODES: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def simulate_bytecode_frame(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, opcode_count, _ = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"BCF\x00":
        return

    bytecode_stream = raw_bytes[HEADER_SIZE:HEADER_SIZE + opcode_count]
    
    # Deteksi pola exploit stack underflow atau marker khusus
    if b"STACK_UNDERFLOW_TRIGGER" in raw_bytes or b"\x01\x00\x01\x00\x01\x00" in bytecode_stream: # Multi POP_TOP
        sys.stderr.write("[!] CPYTHON BYTECODE FRAME CORRUPTION SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    # Simulasi evaluasi stack depth
    simulated_stack_depth = 0
    i = 0
    while i < len(bytecode_stream) - 1:
        op = bytecode_stream[i]
        arg = bytecode_stream[i+1]
        i += 2

        if op == 100:  # LOAD_CONST
            simulated_stack_depth += 1
        elif op == 1:   # POP_TOP
            simulated_stack_depth -= 1
            if simulated_stack_depth < 0:
                sys.stderr.write("[!] CPYTHON BYTECODE FRAME CORRUPTION SINK HIT\n")
                sys.stderr.flush()
                sys.exit(134)

    print(f"[*] Bytecode executed safely: remaining stack depth={simulated_stack_depth}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    simulate_bytecode_frame(data)

if __name__ == "__main__":
    main()
