#!/usr/bin/env python3
import subprocess
import os
import sys

def run_json_diff_target(class_dir, input_file):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    cmd = ["java", "-cp", class_dir, "JsonDifferentialOracle", input_file]
    proc = subprocess.run(cmd, capture_output=True)

    stderr = proc.stderr.decode(errors="ignore")
    is_discrepancy = (proc.returncode != 0) and ("JSON_DIFFERENTIAL_DISCREPANCY_DETECTED" in stderr or "IllegalStateException" in stderr)

    return {
        "returncode": proc.returncode,
        "discrepancy_detected": is_discrepancy,
        "stdout": proc.stdout.decode(errors="ignore"),
        "stderr": stderr
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 diff_json_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_json_diff_target(sys.argv[1], sys.argv[2])
    print(res)
