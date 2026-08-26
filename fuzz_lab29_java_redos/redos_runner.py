#!/usr/bin/env python3
import subprocess
import os
import sys
import time

def run_redos_target(class_dir, input_file, timeout_sec=2.0):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    cmd = ["java", "-cp", class_dir, "RedosValidator", input_file]
    start_t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        elapsed = time.time() - start_t
        stderr = proc.stderr.decode(errors="ignore")
        is_violation = (proc.returncode != 0) and ("REDOS_RESOURCE_EXHAUSTION_VIOLATION" in stderr or "RuntimeException" in stderr)
        return {
            "returncode": proc.returncode,
            "violation_detected": is_violation,
            "elapsed_sec": round(elapsed, 4),
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -9,
            "violation_detected": True,
            "elapsed_sec": timeout_sec,
            "stdout": "",
            "stderr": "TIMEOUT: Regex execution hung"
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 redos_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_redos_target(sys.argv[1], sys.argv[2])
    print(res)
