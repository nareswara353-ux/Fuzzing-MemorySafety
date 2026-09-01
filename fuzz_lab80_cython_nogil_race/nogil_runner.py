#!/usr/bin/env python3
import os
import subprocess
import sys

def run_nogil_target(target_py, input_file, timeout_sec=2.5):
    if not os.path.exists(input_file) or not os.path.exists(target_py):
        return {"status": "error", "message": "Target or input file missing"}

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.abspath(target_py)) + ":" + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run(
            [sys.executable, target_py, input_file],
            capture_output=True,
            timeout=timeout_sec,
            env=env
        )
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("CYTHON NOGIL MEMORY BOUNDARY VIOLATION SINK HIT" in stderr)
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
            "stderr": "TIMEOUT: Native thread race deadlock"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 nogil_runner.py <target.py> <input_file>")
        sys.exit(1)
    res = run_nogil_target(sys.argv[1], sys.argv[2])
    print(res)
