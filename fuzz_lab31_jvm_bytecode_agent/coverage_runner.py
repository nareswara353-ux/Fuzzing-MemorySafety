#!/usr/bin/env python3
import subprocess
import os
import sys

def run_agent_target(class_dir, input_file, cov_dump="/tmp/jvm_coverage.bin"):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    if os.path.exists(cov_dump):
        os.remove(cov_dump)

    cmd = ["java", "-cp", class_dir, "TargetApp", input_file]
    proc = subprocess.run(cmd, capture_output=True)

    branches_hit = 0
    if os.path.exists(cov_dump):
        with open(cov_dump, "rb") as f:
            map_bytes = f.read()
            branches_hit = sum(1 for b in map_bytes if b > 0)

    stderr = proc.stderr.decode(errors="ignore")
    is_crash = (proc.returncode != 0) and ("JVM_BRANCH_TARGET_CRASH_SINK" in stderr or "RuntimeException" in stderr)

    return {
        "returncode": proc.returncode,
        "crashed": is_crash,
        "branches_hit": branches_hit,
        "stdout": proc.stdout.decode(errors="ignore"),
        "stderr": stderr
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 coverage_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_agent_target(sys.argv[1], sys.argv[2])
    print(res)
