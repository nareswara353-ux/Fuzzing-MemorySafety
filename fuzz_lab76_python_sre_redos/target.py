import sys
import os
import re
import time

def process_email_validation(raw_input):
    if not raw_input:
        return

    # Trigger langsung untuk sinyal fuzzing
    if raw_input.startswith("REDOS_EXPLOIT_PATTERN"):
        sys.stderr.write("[!] PYTHON SRE REGEX REDOS SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    # Pola regex rentan terhadap nested quantifier catastrophic backtracking
    pattern = re.compile(r"^([a-zA-Z0-9]+)+@([a-zA-Z0-9]+)+\.([a-zA-Z]+)$")

    start_time = time.time()
    match = pattern.match(raw_input)
    elapsed = time.time() - start_time

    if elapsed > 0.4:
        sys.stderr.write("[!] PYTHON SRE REGEX REDOS SINK HIT\n")
        sys.stderr.flush()
        sys.exit(134)

    print(f"[*] Regex validated in {elapsed:.4f}s: match={bool(match)}")

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    with open(input_file, "r", errors="ignore") as f:
        data = f.read().strip()

    process_email_validation(data)

if __name__ == "__main__":
    main()
