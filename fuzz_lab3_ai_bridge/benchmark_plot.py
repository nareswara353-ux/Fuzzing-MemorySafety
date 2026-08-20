import os
import csv
import matplotlib
matplotlib.use('Agg')  # Headless backend (mencegah crash GUI/GDK)
import matplotlib.pyplot as plt

def parse_afl_plot_data(filepath):
    if not os.path.exists(filepath):
        return None
    
    time_sec = []
    paths_total = []
    map_size = []
    exec_speed = []
    
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            try:
                t = float(row[0].strip())
                p = int(row[3].strip())
                m = float(row[6].strip().replace('%', ''))
                e = float(row[10].strip())
                
                time_sec.append(t)
                paths_total.append(p)
                map_size.append(m)
                exec_speed.append(e)
            except (IndexError, ValueError):
                continue
                
    return {
        'time': time_sec,
        'paths': paths_total,
        'map_size': map_size,
        'speed': exec_speed
    }

ai_data = parse_afl_plot_data("out_ai/default/plot_data")
vanilla_data = parse_afl_plot_data("out_vanilla/default/plot_data")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot 1: Cumulative Path Discovery
if ai_data and ai_data['time']:
    ax1.plot(ai_data['time'], ai_data['paths'], label='AI-Augmented Mutator (Qwen2.5-Coder)', color='#d62728', linewidth=2)
if vanilla_data and vanilla_data['time']:
    ax1.plot(vanilla_data['time'], vanilla_data['paths'], label='Vanilla AFL++ Baseline', color='#1f77b4', linestyle='--', linewidth=2)

ax1.set_ylabel('Total Discovered Paths (Corpus Count)', fontsize=11)
ax1.set_title('Empirical Comparison: Path Exploration & Throughput Over Time', fontsize=13, fontweight='bold')
ax1.legend(loc='lower right')
ax1.grid(True, linestyle=':', alpha=0.6)

# Plot 2: Throughput
if ai_data and ai_data['time']:
    ax2.plot(ai_data['time'], ai_data['speed'], label='AI IPC Bridge Speed', color='#d62728', alpha=0.8)
if vanilla_data and vanilla_data['time']:
    ax2.plot(vanilla_data['time'], vanilla_data['speed'], label='Vanilla Native Speed', color='#1f77b4', linestyle='--', alpha=0.8)

ax2.set_xlabel('Time Elapsed (seconds)', fontsize=11)
ax2.set_ylabel('Executions / Second', fontsize=11)
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('benchmark_result.png', dpi=300)
print("[+] Clean benchmark plot saved to benchmark_result.png")
