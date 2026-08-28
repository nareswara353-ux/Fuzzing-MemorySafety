#!/usr/bin/env python3
import os
import subprocess
import sys
import time

def run_crypto_target(bin_path, input_file, timeout_sec=3.0):
    if not os.path.exists(input_file) or not os.path.exists(bin_path):
        return {"status": "error", "message": "Binary or input file missing"}

    cmd = [bin_path, input_file]
    start_t = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        elapsed = time.perf_counter() - start_t
        stderr = proc.stderr.decode(errors="ignore")
        crashed = (proc.returncode != 0) or ("CRYPTO_SUBTLE_TIMING_LEAK_SINK" in stderr) or ("CRYPTO TIMING LEAK SINK HIT" in stderr)
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
        print("Usage: python3 crypto_runner.py <bin_path> <input_file>")
        sys.exit(1)
    res = run_crypto_target(sys.argv[1], sys.argv[2])
    print(res)
