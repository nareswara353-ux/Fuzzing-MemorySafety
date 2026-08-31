import sys
import os

sys.path.append(os.getcwd())

try:
    import gil_module
except ImportError:
    import glob
    build_libs = glob.glob("build/lib*")
    if build_libs:
        sys.path.append(os.path.abspath(build_libs[0]))
        import gil_module
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
        res = gil_module.process_concurrency(payload)
        print(f"[*] Concurrency executed safely: {res}")
    except Exception as e:
        print(f"Captured exception: {e}")

if __name__ == "__main__":
    main()
