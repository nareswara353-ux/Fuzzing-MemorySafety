#!/usr/bin/env python3
import subprocess
import os
import sys

def execute_blackbox_target(binary_path, input_payload_path):
    if not os.path.exists(binary_path) or not os.path.exists(input_payload_path):
        return {"status": "error", "message": "Binary or input missing"}

    cmd = [binary_path, input_payload_path]
    proc = subprocess.run(cmd, capture_output=True)

    crashed = proc.returncode != 0
    return {
        "target": binary_path,
        "payload": input_payload_path,
        "returncode": proc.returncode,
        "crashed": crashed,
        "output": proc.stdout.decode(errors="ignore") + proc.stderr.decode(errors="ignore")
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 qemu_runner.py <binary> <input_file>")
        sys.exit(1)
    res = execute_blackbox_target(sys.argv[1], sys.argv[2])
    print(res)
