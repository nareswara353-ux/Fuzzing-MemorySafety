#!/usr/bin/env python3
import subprocess
import os
import sys

def run_concurrency_target(class_dir, input_file, timeout_sec=2.0):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    cmd = ["java", "-cp", class_dir, "ConcurrentService", input_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        stderr = proc.stderr.decode(errors="ignore")
        is_violation = (proc.returncode != 0) and ("CONCURRENCY_DEADLOCK_DETECTED" in stderr or "IllegalStateException" in stderr)
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
            "stderr": "TIMEOUT: Concurrency deadlock detected via watchdog timeout"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 concurrency_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_concurrency_target(sys.argv[1], sys.argv[2])
    print(res)
