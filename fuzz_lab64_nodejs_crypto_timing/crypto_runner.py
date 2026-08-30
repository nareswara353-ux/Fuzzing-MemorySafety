#!/usr/bin/env python3
import os
import subprocess
import sys
import time

def run_crypto_target(target_js, input_file, timeout_sec=3.0):
    if not os.path.exists(input_file) or not os.path.exists(target_js):
        return {"status": "error", "message": "Target JS or input file missing"}

    cmd = ["node", target_js, input_file]
    start_t = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        elapsed = time.perf_counter() - start_t
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("NODEJS CRYPTO TIMING SINK HIT" in stderr)
        return {
            "returncode": proc.returncode,
            "crashed": crashed,
            "elapsed_sec": elapsed,
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -9,
            "crashed": True,
            "elapsed_sec": timeout_sec,
            "stdout": "",
            "stderr": "TIMEOUT"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 crypto_runner.py <target.js> <input_file>")
        sys.exit(1)
    res = run_crypto_target(sys.argv[1], sys.argv[2])
    print(res)
