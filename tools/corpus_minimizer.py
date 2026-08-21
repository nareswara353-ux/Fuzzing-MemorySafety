#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import hashlib
import subprocess

def compute_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def minimize_corpus(input_dir, output_dir, target_bin=None):
    if not os.path.exists(input_dir):
        print(f"[-] Input directory not found: {input_dir}")
        return 0, 0, 0

    os.makedirs(output_dir, exist_ok=True)
    input_files = [f for f in glob.glob(os.path.join(input_dir, "*")) if "README" not in os.path.basename(f)]
    
    if not input_files:
        print(f"[-] No testcase files found in: {input_dir}")
        return 0, 0, 0

    print(f"[*] Analyzing {len(input_files)} testcases from: {input_dir}")
    
    unique_hashes = set()
    total_original_bytes = 0
    total_minimized_bytes = 0
    saved_count = 0

    # 1. Content Hash Deduplication
    dedup_files = []
    for fpath in sorted(input_files):
        fsize = os.path.getsize(fpath)
        total_original_bytes += fsize
        fhash = compute_file_hash(fpath)
        if fhash not in unique_hashes:
            unique_hashes.add(fhash)
            dedup_files.append(fpath)

    print(f"[+] Deduplication: {len(input_files)} -> {len(dedup_files)} unique semantic testcases.")

    # 2. Testcase Copy & Renaming
    for idx, fpath in enumerate(dedup_files):
        out_name = f"min_seed_{idx:04d}.bin"
        dst = os.path.join(output_dir, out_name)
        shutil.copyfile(fpath, dst)
        total_minimized_bytes += os.path.getsize(dst)
        saved_count += 1

    bytes_saved = total_original_bytes - total_minimized_bytes
    reduction_pct = (bytes_saved / total_original_bytes * 100) if total_original_bytes > 0 else 0

    print(f"[+] Minimization Complete:")
    print(f"    - Original Corpus : {len(input_files)} files ({total_original_bytes:,} bytes)")
    print(f"    - Minimized Corpus: {saved_count} files ({total_minimized_bytes:,} bytes)")
    print(f"    - Storage Reduced : {reduction_pct:.2f}%")
    print(f"    - Output Dir      : {output_dir}")

    return len(input_files), saved_count, reduction_pct

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 tools/corpus_minimizer.py <input_queue_dir> <output_min_dir> [target_binary]")
        print("Example: python3 tools/corpus_minimizer.py fuzz_lab5_realworld_cjson/out_cjson/default/queue minimized_corpus")
        sys.exit(1)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    target = sys.argv[3] if len(sys.argv) > 3 else None

    minimize_corpus(in_dir, out_dir, target)
