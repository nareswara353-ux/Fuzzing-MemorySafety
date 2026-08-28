#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

def patch_and_verify_go(src_path, crash_path, seed_path):
    if not os.path.exists(src_path) or not os.path.exists(crash_path):
        return {"status": "error", "message": "Source or crash file not found"}

    with open(src_path, "r") as f:
        original_code = f.read()

    unsafe_snippet = "copyLen := len(data)\n\n\tfor i := 0; i < copyLen; i++ {"
    safe_snippet = "copyLen := len(data)\n\tif copyLen > len(fixedBuf) {\n\t\tcopyLen = len(fixedBuf)\n\t}\n\n\tfor i := 0; i < copyLen; i++ {"

    if unsafe_snippet not in original_code:
        return {"status": "error", "message": "Target pattern not found in source"}

    patched_code = original_code.replace(unsafe_snippet, safe_snippet)

    patch_diff = """--- vuln_target.go (Original)
+++ vuln_target.go (Patched)
@@ -12,2 +12,5 @@
 	copyLen := len(data)
+	if copyLen > len(fixedBuf) {
+		copyLen = len(fixedBuf)
+	}
"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_src = os.path.join(tmp_dir, "vuln_target.go")
        tmp_mod = os.path.join(tmp_dir, "go.mod")
        tmp_bin = os.path.join(tmp_dir, "patched_target_bin")

        with open(tmp_src, "w") as f:
            f.write(patched_code)
        with open(tmp_mod, "w") as f:
            f.write("module temp_patch\n\ngo 1.21\n")

        compile_res = subprocess.run(["go", "build", "-o", tmp_bin, "."], cwd=tmp_dir, capture_output=True)
        if compile_res.returncode != 0:
            return {"status": "compile_error", "error": compile_res.stderr.decode()}

        test_crash = subprocess.run([tmp_bin, crash_path], capture_output=True)
        crash_fixed = (test_crash.returncode == 0)

        liveness_ok = True
        if os.path.exists(seed_path):
            test_seed = subprocess.run([tmp_bin, seed_path], capture_output=True)
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
        print("Usage: python3 go_auto_patcher.py <source.go> <crash_poc.bin> <valid_seed.bin>")
        sys.exit(1)
    res = patch_and_verify_go(sys.argv[1], sys.argv[2], sys.argv[3])
    print(res)
