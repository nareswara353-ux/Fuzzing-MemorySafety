import sys
import os
import struct

# Struktur Header: [MAGIC: 4B "NMP\x00"][ROWS: 2B][COLS: 2B][STRIDE_ROW: 2B][STRIDE_COL: 2B][PAYLOAD: 32B]
HEADER_FORMAT = "<4sHHHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
BUFFER_CAPACITY = 32

def process_strided_buffer(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE + BUFFER_CAPACITY:
        return

    magic, rows, cols, stride_row, stride_col = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"NMP\x00":
        return

    buffer_data = raw_bytes[HEADER_SIZE:HEADER_SIZE + BUFFER_CAPACITY]

    # Hitung batas akses maksimum berdasarkan strides
    if rows > 0 and cols > 0:
        max_offset = ((rows - 1) * stride_row) + ((cols - 1) * stride_col)
    else:
        max_offset = 0

    # VULNERABILITY SINK: Akses melampaui kapasitas buffer aktual (Out-of-Bounds Strided Access)
    if max_offset >= BUFFER_CAPACITY or stride_row > 100 or b"CORRUPT_STRIDES" in buffer_data:
        sys.stderr.write("[!] NUMPY BUFFER PROTOCOL STRIDED CORRUPTION SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    print(f"[*] Buffer safely mapped: shape=({rows},{cols}), max_offset={max_offset}/{BUFFER_CAPACITY}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_strided_buffer(data)

if __name__ == "__main__":
    main()
