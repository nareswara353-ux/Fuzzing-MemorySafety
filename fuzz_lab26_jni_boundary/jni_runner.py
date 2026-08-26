#!/usr/bin/env python3
import subprocess
import os
import sys

def run_jni_target(class_dir, input_file):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file missing"}

    cmd = ["java", f"-Djava.library.path={class_dir}", "-cp", class_dir, "NativeBridge", input_file]
    proc = subprocess.run(cmd, capture_output=True)

    crashed = proc.returncode != 0
    return {
        "returncode": proc.returncode,
        "crashed": crashed,
        "stdout": proc.stdout.decode(errors="ignore"),
        "stderr": proc.stderr.decode(errors="ignore")
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 jni_runner.py <class_dir> <input_file>")
        sys.exit(1)
    res = run_jni_target(sys.argv[1], sys.argv[2])
    print(res)
