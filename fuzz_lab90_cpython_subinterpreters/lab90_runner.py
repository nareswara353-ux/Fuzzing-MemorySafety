#!/usr/bin/env python3
import sys
import subprocess
import os
import tempfile

def run_target(input_data, buggy=True):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(input_data)
        temp_file = f.name
    try:
        func = 'run_code_buggy' if buggy else 'run_code_safe'
        script = f"""
import subinterpreter_target
import sys
with open('{temp_file}', 'r') as f:
    code = f.read()
try:
    result = subinterpreter_target.{func}(code)
except Exception as e:
    print(f"Exception: {{e}}", file=sys.stderr)
    sys.exit(1)
# Jika hasil tidak None, kita paksa gunakan untuk memicu crash (jika ada bug)
if result is not None:
    print(str(result))
"""
        proc = subprocess.Popen([sys.executable, '-c', script],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=5)
        return proc.returncode, stdout, stderr
    finally:
        os.unlink(temp_file)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: lab90_runner.py <input_file> [--safe]")
        sys.exit(1)
    input_file = sys.argv[1]
    buggy = True
    if '--safe' in sys.argv:
        buggy = False
    with open(input_file, 'r') as f:
        data = f.read()
    ret, out, err = run_target(data, buggy)
    print(f"Return code: {ret}")
    if out:
        print(f"STDOUT: {out.decode()}")
    if err:
        print(f"STDERR: {err.decode()}")
    if ret < 0:  # terminated by signal
        print(f"CRASH detected (signal {-ret})")
        sys.exit(1)
    elif ret != 0:
        print(f"Error exit code {ret}")
        sys.exit(1)
    else:
        sys.exit(0)
