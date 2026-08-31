#!/usr/bin/env python3
import os
import subprocess
import sys

def run_sandbox_target(target_py, input_file, timeout_sec=2.5):
    if not os.path.exists(input_file) or not os.path.exists(target_py):
        return {"status": "error", "message": "Target or input file missing"}

    try:
        proc = subprocess.run(
            [sys.executable, target_py, input_file],
            capture_output=True,
            timeout=timeout_sec
        )
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("PYTHON SANDBOX ESCAPE SINK HIT" in stderr)
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
            "stderr": "TIMEOUT: Infinite loop detected in sandbox execution"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 sandbox_runner.py <target.py> <input_file>")
        sys.exit(1)
    res = run_sandbox_target(sys.argv[1], sys.argv[2])
    print(res)
