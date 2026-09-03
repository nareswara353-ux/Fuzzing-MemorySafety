import sys
import os
import struct

# Format Header: [MAGIC: 4B "UNI\x00"][ENCODING_FLAG: 2B][PAYLOAD_LEN: 2B][DATA: N Bytes]
HEADER_FORMAT = "<4sHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def process_unicode_stream(raw_bytes):
    if len(raw_bytes) < HEADER_SIZE:
        return

    magic, enc_flag, payload_len = struct.unpack(HEADER_FORMAT, raw_bytes[:HEADER_SIZE])
    if magic != b"UNI\x00":
        return

    payload = raw_bytes[HEADER_SIZE:HEADER_SIZE + payload_len]

    # VULNERABILITY SINK: Lone surrogate handling atau injeksi surrogateescape berbahaya
    if b"\xed\xa0\x80" in payload or b"TRIGGER_UNICODE_CRASH" in payload:  # UTF-8 encoding of U+D800
        sys.stderr.write("[!] PYTHON UNICODE SURROGATE DECODER SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    try:
        # Simulasi decoding string fleksibel PEP 393
        if enc_flag == 1:
            decoded = payload.decode("utf-8", errors="surrogateescape")
        else:
            decoded = payload.decode("utf-8", errors="strict")

        # Cek apakah ada lone surrogate yang lolos ke level representasi karakter
        for ch in decoded:
            code_point = ord(ch)
            if 0xD800 <= code_point <= 0xDFFF:
                sys.stderr.write("[!] PYTHON UNICODE SURROGATE DECODER SINK HIT\n")
                sys.stderr.flush()
                sys.exit(134)

        print(f"[*] Unicode processed safely: length={len(decoded)}")
    except UnicodeDecodeError:
        pass

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    process_unicode_stream(data)

if __name__ == "__main__":
    main()
