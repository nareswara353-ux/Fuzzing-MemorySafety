import sys
import os
import ast

def safe_eval_sandbox(code_str):
    # Blacklist filter naif yang rentan terhadap bypass traversal objek
    restricted_keywords = ["import", "eval", "exec", "compile", "open"]
    for kw in restricted_keywords:
        if kw in code_str:
            return

    # Deteksi eksplisit exploit PyJail traversal
    if "__subclasses__" in code_str or "__globals__" in code_str or "__builtins__" in code_str:
        sys.stderr.write("[!] PYTHON SANDBOX ESCAPE SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    # Menjalankan evaluasi dalam namespace terbatas
    sandbox_globals = {"__builtins__": {}}
    try:
        parsed_ast = ast.parse(code_str, mode="eval")
        res = eval(compile(parsed_ast, "<sandbox>", "eval"), sandbox_globals, {})
        return res
    except Exception:
        pass

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "r", errors="ignore") as f:
        code_str = f.read().strip()

    if len(code_str) == 0:
        return

    safe_eval_sandbox(code_str)
    print("[*] Expression evaluated safely in sandbox")

if __name__ == "__main__":
    main()
