#!/usr/bin/env python3
import os
import subprocess
import sys

def run_cext_target(target_py, input_file, timeout_sec=2.0):
    if not os.path.exists(input_file) or not os.path.exists(target_py):
        return {"status": "error", "message": "Target or input missing"}

    # Jalankan dengan environment path yang benar
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + ":" + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run([sys.executable, target_py, input_file], 
                             capture_output=True, timeout=timeout_sec, env=env)
        
        stderr = proc.stderr.decode(errors="ignore")
        # Segmentation fault biasanya return code negatif (-11)
        crashed = (proc.returncode != 0) or ("BUFFER OVERFLOW HIT" in stderr)
        
        return {
            "returncode": proc.returncode,
            "crashed": crashed,
            "stderr": stderr
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -9, "crashed": False, "stderr": "TIMEOUT"}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    print(run_cext_target(sys.argv[1], sys.argv[2]))
