import sys
import os
import struct

sys.path.append(os.getcwd())

try:
    import nogil_module
except ImportError:
    import glob
    build_libs = glob.glob("build/lib*")
    if build_libs:
        sys.path.append(os.path.abspath(build_libs[0]))
        import nogil_module
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

    if len(data) < 4:
        return

    offset = struct.unpack("<i", data[:4])[0]
    payload_str = data[4:].decode(errors="ignore")

    try:
        res = nogil_module.execute_nogil_race(offset, payload_str)
        print(f"[*] Nogil execution finished safely: counter={res}")
    except Exception as e:
        print(f"Captured exception: {e}")

if __name__ == "__main__":
    main()
