import sys
import os
import struct

sys.path.append(os.getcwd())

try:
    import pymalloc_module
except ImportError:
    import glob
    build_libs = glob.glob("build/lib*")
    if build_libs:
        sys.path.append(os.path.abspath(build_libs[0]))
        import pymalloc_module
    else:
        print("Module not found. Build it first.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "rb") as f:
        data = f.read()

    if len(data) < 8:
        return

    alloc_size, write_len = struct.unpack("<ii", data[:8])
    payload_str = data[8:].decode(errors="ignore")

    try:
        res = pymalloc_module.allocate_and_mutate(alloc_size, write_len, payload_str)
        print(f"[*] Pymalloc pool executed safely: {res}")
    except Exception as e:
        print(f"Captured exception: {e}")

if __name__ == "__main__":
    main()
