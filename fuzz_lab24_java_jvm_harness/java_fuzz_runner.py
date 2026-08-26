#!/usr/bin/env python3
import subprocess
import os
import sys

def execute_java_target(class_dir, class_name, input_file):
    if not os.path.exists(input_file):
        return {"status": "error", "message": "Input file not found"}

    cmd = ["java", "-cp", class_dir, class_name, input_file]
    proc = subprocess.run(cmd, capture_output=True)

    stdout = proc.stdout.decode(errors="ignore")
    stderr = proc.stderr.decode(errors="ignore")
    
    is_jvm_crash = (proc.returncode != 0) and ("Exception in thread" in stderr or "CRITICAL_JVM_EXCEPTION" in stderr)

    return {
        "returncode": proc.returncode,
        "crashed": is_jvm_crash,
        "stdout": stdout,
        "stderr": stderr
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 java_fuzz_runner.py <class_dir> <class_name> <input_file>")
        sys.exit(1)
    res = execute_java_target(sys.argv[1], sys.argv[2], sys.argv[3])
    print(res)
