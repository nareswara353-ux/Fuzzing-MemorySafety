#!/usr/bin/env python3
import subprocess
import os
import sys

def run_xxe_target(class_dir, input_file):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    cmd = ["java", "-cp", class_dir, "XxeTargetParser", input_file]
    proc = subprocess.run(cmd, capture_output=True)

    stderr = proc.stderr.decode(errors="ignore")
    is_violation = (proc.returncode != 0) and ("XXE_CRITICAL_RESOURCE_EXHAUSTION" in stderr or "SecurityException" in stderr)

    return {
        "returncode": proc.returncode,
        "violation_detected": is_violation,
        "stdout": proc.stdout.decode(errors="ignore"),
        "stderr": stderr
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 xxe_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_xxe_target(sys.argv[1], sys.argv[2])
    print(res)
