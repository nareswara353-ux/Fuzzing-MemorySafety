#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

def patch_and_verify_java(src_path, crash_path, seed_path):
    if not os.path.exists(src_path) or not os.path.exists(crash_path):
        return {"status": "error", "message": "Source or crash file not found"}

    with open(src_path, "r") as f:
        original_code = f.read()

    unsafe_snippet = "int limit = data.length;\n        for (int i = 0; i < limit; i++) {"
    safe_snippet = "int limit = Math.min(data.length, buffer.length);\n        for (int i = 0; i < limit; i++) {"

    if unsafe_snippet not in original_code:
        return {"status": "error", "message": "Target pattern not found in source"}

    patched_code = original_code.replace(unsafe_snippet, safe_snippet)

    patch_diff = """--- VulnArrayHandler.java (Original)
+++ VulnArrayHandler.java (Patched)
@@ -7,2 +7,2 @@
-        int limit = data.length;
+        int limit = Math.min(data.length, buffer.length);
"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_src = os.path.join(tmp_dir, "VulnArrayHandler.java")
        with open(tmp_src, "w") as f:
            f.write(patched_code)

        compile_res = subprocess.run(["javac", tmp_src], capture_output=True)
        if compile_res.returncode != 0:
            return {"status": "compile_error", "error": compile_res.stderr.decode()}

        test_crash = subprocess.run(["java", "-cp", tmp_dir, "VulnArrayHandler", crash_path], capture_output=True)
        crash_fixed = (test_crash.returncode == 0)

        liveness_ok = True
        if os.path.exists(seed_path):
            test_seed = subprocess.run(["java", "-cp", tmp_dir, "VulnArrayHandler", seed_path], capture_output=True)
            liveness_ok = (test_seed.returncode == 0)

    patch_file_path = os.path.splitext(src_path)[0] + "_auto_fix.patch"
    if crash_fixed and liveness_ok:
        with open(patch_file_path, "w") as pf:
            pf.write(patch_diff)

    return {
        "source_file": src_path,
        "patch_applied": True,
        "crash_fixed": crash_fixed,
        "no_regression": liveness_ok,
        "patch_file": patch_file_path if (crash_fixed and liveness_ok) else None,
        "patch_diff": patch_diff
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 java_auto_patcher.py <source.java> <crash_poc.bin> <valid_seed.bin>")
        sys.exit(1)
    res = patch_and_verify_java(sys.argv[1], sys.argv[2], sys.argv[3])
    print(res)
