import sys
import os

# Menambahkan direktori build ke path agar bisa import .so
sys.path.append(os.getcwd())

try:
    import vuln_module
except ImportError:
    # Coba cari di subfolder build
    import glob
    build_libs = glob.glob("build/lib*")
    if build_libs:
        sys.path.append(os.path.abspath(build_libs[0]))
        import vuln_module
    else:
        print("Module not found. Build it first.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "r", errors="ignore") as f:
        payload = f.read().strip()

    try:
        vuln_module.process_data(payload)
        print("[*] Extension call finished safely")
    except Exception as e:
        print(f"Captured exception: {e}")

if __name__ == "__main__":
    main()
