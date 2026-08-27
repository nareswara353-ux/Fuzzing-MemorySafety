#!/usr/bin/env python3
import os
import subprocess
import sys

def run_overflow_target(bin_path, input_file):
    if not os.path.exists(input_file) or not os.path.exists(bin_path):
        return {"status": "error", "message": "Binary or input file missing"}

    cmd = [bin_path, input_file]
    proc = subprocess.run(cmd, capture_output=True)

    stderr = proc.stderr.decode(errors="ignore")
    panicked = (proc.returncode != 0) and ("INTEGER OVERFLOW SINK HIT" in stderr or "overflow" in stderr or "panicked" in stderr)

    return {
        "returncode": proc.returncode,
        "panicked": panicked,
        "stdout": proc.stdout.decode(errors="ignore"),
        "stderr": stderr
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 overflow_runner.py <bin_path> <input_file>")
        sys.exit(1)
    res = run_overflow_target(sys.argv[1], sys.argv[2])
    print(res)
