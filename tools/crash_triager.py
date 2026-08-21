#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import re
import json

def triage_binary(binary_path, crash_dir):
    if not os.path.exists(binary_path):
        print(f"[-] Binary not found: {binary_path}")
        return []
    
    crash_files = [f for f in glob.glob(os.path.join(crash_dir, "*")) if "README" not in f]
    if not crash_files:
        print(f"[-] No crash files found in: {crash_dir}")
        return []
    
    print(f"[+] Found {len(crash_files)} crash artifacts. Starting automated ASan triage...")
    results = []

    for crash_file in sorted(crash_files):
        cmd = [os.path.abspath(binary_path), os.path.abspath(crash_file)]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stderr = proc.stderr

        # Ekstraksi metadata AddressSanitizer
        crash_type_match = re.search(r"ERROR: AddressSanitizer: ([\w\-]+) on address (0x[0-9a-fA-F]+)", stderr)
        access_match = re.search(r"(READ|WRITE) of size (\d+) at (0x[0-9a-fA-F]+)", stderr)
        location_match = re.search(r"#1\s+(0x[0-9a-fA-F]+)\s+in\s+([\w\:]+)\s+([^\n]+)", stderr)

        triage_entry = {
            "crash_file": os.path.basename(crash_file),
            "crash_type": crash_type_match.group(1) if crash_type_match else "Unknown / SIGSEGV",
            "fault_address": crash_type_match.group(2) if crash_type_match else "N/A",
            "operation": access_match.group(1) if access_match else "N/A",
            "access_size": int(access_match.group(2)) if access_match else 0,
            "root_cause_func": location_match.group(2) if location_match else "N/A",
            "source_location": location_match.group(3).strip() if location_match else "N/A",
            "return_code": proc.returncode
        }
        results.append(triage_entry)
        print(f"    [*] Triaged: {triage_entry['crash_file']} -> {triage_entry['crash_type']} in {triage_entry['root_cause_func']}")

    return results

def generate_markdown_report(results, output_file="TRIAGE_REPORT.md"):
    md = "# Automated Vulnerability Triage Report\n\n"
    md += f"> **Total Unique Crashes Analyzed:** {len(results)}\n\n"
    md += "| Crash Artifact | Vulnerability Class | Operation | Access Size | Root Cause Function | Source Line |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for r in results:
        md += f"| `{r['crash_file']}` | **{r['crash_type']}** | `{r['operation']}` | `{r['access_size']} bytes` | `{r['root_cause_func']}` | `{r['source_location']}` |\n"
    
    with open(output_file, "w") as f:
        f.write(md)
    print(f"[+] Generated structured triage report: {output_file}")

if __name__ == "__main__":
    target_bin = sys.argv[1] if len(sys.argv) > 1 else "fuzz_lab6_adaptive_stagnation/target_fuzz"
    crashes_path = sys.argv[2] if len(sys.argv) > 2 else "fuzz_lab6_adaptive_stagnation/out_lab6/default/crashes"
    
    triage_data = triage_binary(target_bin, crashes_path)
    if triage_data:
        generate_markdown_report(triage_data)
        with open("triage_results.json", "w") as jf:
            json.dump(triage_data, jf, indent=2)
        print("[+] JSON data exported to: triage_results.json")
