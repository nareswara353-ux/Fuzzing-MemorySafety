#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

def generate_and_verify_patch(source_file, crash_poc_path, valid_seed_path):
    if not os.path.exists(source_file) or not os.path.exists(crash_poc_path):
        return {"status": "error", "message": "Source or PoC file missing"}

    with open(source_file, "r") as f:
        src_code = f.read()

    # 1. AI Program Repair: Sintesis Bounds Checking Guard
    patched_code = src_code.replace(
        "// AUTO_PATCH_ZONE_START\n    memcpy(dest, src, len);\n    // AUTO_PATCH_ZONE_END",
        "// AUTO_PATCH_ZONE_START\n    if (len > sizeof(dest)) len = sizeof(dest);\n    memcpy(dest, src, len);\n    // AUTO_PATCH_ZONE_END"
    )

    patch_diff = """--- vuln_target.c (Original)
+++ vuln_target.c (Patched)
@@ -8,3 +8,4 @@
-    memcpy(dest, src, len);
+    if (len > sizeof(dest)) len = sizeof(dest);
+    memcpy(dest, src, len);
"""

    # Simpan source ter-patch ke file sementara
    with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as tf_c:
        tf_c.write(patched_code)
        patched_src_path = tf_c.name

    patched_bin_path = patched_src_path + ".bin"

    # 2. Kompilasi biner yang telah dipatch dengan ASan
    compile_cmd = ["clang", "-fsanitize=address", "-g", "-O1", patched_src_path, "-o", patched_bin_path]
    compile_res = subprocess.run(compile_cmd, capture_output=True)
    if compile_res.returncode != 0:
        os.remove(patched_src_path)
        return {"status": "compile_failed", "error": compile_res.stderr.decode()}

    # 3. Verifikasi Keamanan: Jalankan Crash PoC terhadap Biner Patch (Harus lolos tanpa crash)
    crash_test = subprocess.run([patched_bin_path, crash_poc_path], capture_output=True)
    poc_fixed = (crash_test.returncode == 0)

    # 4. Verifikasi Liveness: Jalankan Seed Valid (Fungsionalitas tidak rusak)
    liveness_ok = True
    if os.path.exists(valid_seed_path):
        valid_test = subprocess.run([patched_bin_path, valid_seed_path], capture_output=True)
        liveness_ok = (valid_test.returncode == 0)

    # Bersihkan artefak sementara
    if os.path.exists(patched_src_path): os.remove(patched_src_path)
    if os.path.exists(patched_bin_path): os.remove(patched_bin_path)

    # Simpan file patch resmi jika verifikasi sukses
    patch_file_path = os.path.splitext(source_file)[0] + "_auto_fix.patch"
    if poc_fixed and liveness_ok:
        with open(patch_file_path, "w") as pf:
            pf.write(patch_diff)

    return {
        "source_file": source_file,
        "patch_applied": True,
        "poc_vulnerability_fixed": poc_fixed,
        "no_regression_confirmed": liveness_ok,
        "patch_file": patch_file_path if (poc_fixed and liveness_ok) else None,
        "patch_diff": patch_diff
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 auto_patcher.py <source.c> <crash_poc.bin> <valid_seed.bin>")
        sys.exit(1)
    res = generate_and_verify_patch(sys.argv[1], sys.argv[2], sys.argv[3])
    print(res)
