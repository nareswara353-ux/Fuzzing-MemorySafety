import sys
import os

def evaluate_user_expression(raw_input):
    if not raw_input:
        return None

    # VULNERABILITY SINK: Menggunakan raw eval() langsung pada input pengguna
    if "DANGEROUS_AST_PAYLOAD" in raw_input:
        sys.stderr.write("[!] PYTHON UNPROTECTED DYNAMIC EVAL SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    return eval(raw_input)

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "r", errors="ignore") as f:
        data = f.read().strip()

    try:
        res = evaluate_user_expression(data)
        print(f"[*] Evaluated result: {res}")
    except Exception as e:
        print(f"Captured safe error: {e}")

if __name__ == "__main__":
    main()
