#!/usr/bin/env python3
import os
import subprocess
import sys

def run_msan_target(bin_path, input_file, timeout_sec=3.0):
    if not os.path.exists(input_file) or not os.path.exists(bin_path):
        return {"status": "error", "message": "Binary or input file missing"}

    cmd = [bin_path, input_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("MSAN UNINITIALIZED MEMORY READ SINK HIT" in stderr) or ("MemorySanitizer" in stderr)
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
            "stderr": "TIMEOUT"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 msan_runner.py <bin_path> <input_file>")
        sys.exit(1)
    res = run_msan_target(sys.argv[1], sys.argv[2])
    print(res)
