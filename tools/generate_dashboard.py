#!/usr/bin/env python3
import os
import glob
import re
import json
from datetime import datetime

def parse_fuzzer_stats(stats_path):
    data = {}
    if not os.path.exists(stats_path):
        return data
    with open(stats_path, "r") as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    return data

def scan_all_experiments(base_dir="."):
    experiments = []
    # Cari semua direktori fuzzer_stats di seluruh lab
    stat_files = glob.glob(os.path.join(base_dir, "**/fuzzer_stats"), recursive=True)
    
    for sf in stat_files:
        stats = parse_fuzzer_stats(sf)
        lab_folder = sf.split(os.sep)[1] if len(sf.split(os.sep)) > 1 else "Unknown"
        out_dir = os.path.dirname(sf)
        
        # Hitung corpus queue dan crashes
        queue_count = len([f for f in glob.glob(os.path.join(out_dir, "queue", "id:*"))])
        crash_count = len([f for f in glob.glob(os.path.join(out_dir, "crashes", "id:*")) if "README" not in f])
        
        # Ekstraksi metrik penting
        execs = stats.get("execs_done", "0")
        exec_speed = stats.get("execs_per_sec", "0")
        map_density = stats.get("bitmap_cvg", stats.get("map_size", "N/A"))
        stability = stats.get("stability", "100.00%")
        runtime = stats.get("run_time", "N/A")
        
        experiments.append({
            "lab": lab_folder,
            "target": stats.get("target_mode", stats.get("command_line", "target")).split()[-1],
            "runtime_seconds": stats.get("run_time", "0"),
            "total_execs": execs,
            "exec_speed": exec_speed,
            "corpus_count": queue_count,
            "unique_crashes": crash_count,
            "map_density": map_density,
            "stability": stability
        })
    return experiments

def generate_html_dashboard(experiments, output_html="report_dashboard.html"):
    rows = ""
    for exp in experiments:
        crash_badge = f"<span class='badge badge-danger'>{exp['unique_crashes']} Crashes</span>" if exp['unique_crashes'] > 0 else "<span class='badge badge-success'>0 Crashes</span>"
        rows += f"""
        <tr>
            <td><strong>{exp['lab']}</strong></td>
            <td><code>{exp['target']}</code></td>
            <td>{exp['total_execs']}</td>
            <td>{exp['exec_speed']}/sec</td>
            <td><span class='badge badge-info'>{exp['corpus_count']} seeds</span></td>
            <td>{exp['map_density']}</td>
            <td>{crash_badge}</td>
            <td>{exp['stability']}</td>
        </tr>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compiler-Guided Neural Fuzzing | Unified Telemetry Dashboard</title>
    <style>
        :root {{
            --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --text-muted: #94a3b8;
            --accent: #38bdf8; --border: #334155; --success: #22c55e; --danger: #ef4444;
        }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }}
        h1 {{ font-size: 1.8rem; margin: 0; color: var(--accent); }}
        p.subtitle {{ color: var(--text-muted); margin: 0.5rem 0 0 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.2rem; }}
        .card .title {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        .card .value {{ font-size: 1.8rem; font-weight: bold; margin-top: 0.5rem; color: var(--text); }}
        table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: #0f172a; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; }}
        tr:hover {{ background: rgba(255,255,255,0.02); }}
        code {{ background: #0b0f19; padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace; color: #f472b6; }}
        .badge {{ padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }}
        .badge-info {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; }}
        .badge-success {{ background: rgba(34, 197, 94, 0.15); color: #22c55e; }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; }}
        footer {{ margin-top: 3rem; text-align: center; color: var(--text-muted); font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 Compiler-Guided Neural Fuzzing Framework</h1>
            <p class="subtitle">Unified Experimental Telemetry & Empirical Benchmark Aggregator | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <div class="grid">
            <div class="card">
                <div class="title">Total Benchmark Labs</div>
                <div class="value">{len(experiments)}</div>
            </div>
            <div class="card">
                <div class="title">Total Executions</div>
                <div class="value">{sum(int(e['total_execs']) for e in experiments if e['total_execs'].isdigit()):,}</div>
            </div>
            <div class="card">
                <div class="title">Total Discovered Seeds</div>
                <div class="value">{sum(e['corpus_count'] for e in experiments):,}</div>
            </div>
            <div class="card">
                <div class="title">Vulnerabilities Caught</div>
                <div class="value" style="color: var(--danger);">{sum(e['unique_crashes'] for e in experiments)}</div>
            </div>
        </div>

        <h2>📊 Empirical Experiment Matrix</h2>
        <table>
            <thead>
                <tr>
                    <th>Lab Module</th>
                    <th>Target Binary</th>
                    <th>Total Execs</th>
                    <th>Speed</th>
                    <th>Corpus Queue</th>
                    <th>Map Coverage</th>
                    <th>Crash Status</th>
                    <th>Stability</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <footer>
            Master / Ph.D. Research Track &mdash; Software & Systems Security &bull; Automated Telemetry Engine
        </footer>
    </div>
</body>
</html>
"""
    with open(output_html, "w") as f:
        f.write(html)
    print(f"[+] Generated Unified Dashboard: {output_html}")

if __name__ == "__main__":
    exps = scan_all_experiments()
    if exps:
        generate_html_dashboard(exps)
        with open("benchmark_summary.json", "w") as jf:
            json.dump(exps, jf, indent=2)
        print("[+] Telemetry JSON exported: benchmark_summary.json")
    else:
        print("[-] No AFL++ output directories found.")
