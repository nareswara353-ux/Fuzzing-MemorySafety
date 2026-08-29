#!/usr/bin/env python3
import os
import subprocess
import sys

def run_ts_target(compiled_js, input_file, timeout_sec=3.0):
    if not os.path.exists(input_file) or not os.path.exists(compiled_js):
        return {"status": "error", "message": "Compiled JS or input file missing"}

    cmd = ["node", compiled_js, input_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("TYPESCRIPT RUNTIME TYPE CONFUSION SINK HIT" in stderr)
        return {
            "returncode": proc.returncode,
            "crashed": crashed,
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -9,
            "crashed": True,
            "stdout": "",
            "stderr": "TIMEOUT: Infinite loop or execution timeout"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 ts_runner.py <compiled.js> <input_file>")
        sys.exit(1)
    res = run_ts_target(sys.argv[1], sys.argv[2])
    print(res)
