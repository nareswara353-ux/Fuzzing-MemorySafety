#!/usr/bin/env python3
import os
import subprocess
import sys

def run_async_target(bin_path, input_file, timeout_sec=1.5):
    if not os.path.exists(input_file) or not os.path.exists(bin_path):
        return {"status": "error", "message": "Binary or input file missing"}

    cmd = [bin_path, input_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        stderr = proc.stderr.decode(errors="ignore")
        is_violation = (proc.returncode != 0) or ("ASYNC CHANNEL DEADLOCK SINK HIT" in stderr)
        return {
            "returncode": proc.returncode,
            "violation_detected": is_violation,
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -9,
            "violation_detected": True,
            "stdout": "",
            "stderr": "TIMEOUT: Async executor task starvation / channel deadlock detected"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 async_runner.py <bin_path> <input_file>")
        sys.exit(1)
    res = run_async_target(sys.argv[1], sys.argv[2])
    print(res)
