#!/usr/bin/env python3
import os
import subprocess
import sys

def run_worker_target(target_js, input_file, timeout_sec=3.0):
    if not os.path.exists(input_file) or not os.path.exists(target_js):
        return {"status": "error", "message": "Target JS or input file missing"}

    cmd = ["node", target_js, input_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("WORKER THREAD SHARED MEMORY DATA RACE HIT" in stderr)
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
            "stderr": "TIMEOUT: Worker thread deadlock or execution timeout"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 worker_runner.py <target.js> <input_file>")
        sys.exit(1)
    res = run_worker_target(sys.argv[1], sys.argv[2])
    print(res)
