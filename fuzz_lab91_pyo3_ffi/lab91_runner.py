#!/usr/bin/env python3
import sys
import subprocess
import os
import tempfile

def run_target(input_str, buggy=True):
    # Karena modul Rust harus diimpor, kita set PYTHONPATH
    # Kita jalankan dengan Python dan impor modul
    script = f"""
import pyo3_ffi_target
import sys
func = pyo3_ffi_target.get_string_buggy if {buggy} else pyo3_ffi_target.get_string_safe
try:
    result = func({repr(input_str)})
    print(result)
except Exception as e:
    print(f"Exception: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
    env = os.environ.copy()
    # Tambahkan direktori lab ke PYTHONPATH
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    pythonpath = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = lab_dir + (os.pathsep + pythonpath if pythonpath else '')
    proc = subprocess.Popen([sys.executable, '-c', script],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env)
    stdout, stderr = proc.communicate(timeout=5)
    return proc.returncode, stdout, stderr

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: lab91_runner.py <input_string> [--safe]")
        sys.exit(1)
    input_str = sys.argv[1]
    buggy = True
    if '--safe' in sys.argv:
        buggy = False
    ret, out, err = run_target(input_str, buggy)
    print(f"Return code: {ret}")
    if out:
        print(f"STDOUT: {out.decode()}")
    if err:
        print(f"STDERR: {err.decode()}")
    if ret != 0:
        print("CRASH detected" if ret < 0 else "Error exit")
        sys.exit(1)
    else:
        sys.exit(0)
