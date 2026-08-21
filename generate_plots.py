import os
import glob
import matplotlib
matplotlib.use('Agg')  # Menghentikan crash GDK / GUI
import matplotlib.pyplot as plt

plot_file = "fuzz_lab5_realworld_cjson/out_cjson/default/plot_data"

if not os.path.exists(plot_file):
    matches = glob.glob("fuzz_lab5_realworld_cjson/**/plot_data", recursive=True)
    plot_file = matches[0] if matches else None

times, edges, corpus = [], [], []

def clean_num(val):
    val = val.replace('%', '').strip()
    return float(val)

if plot_file and os.path.exists(plot_file):
    print(f"[+] Mem-parsing metrik AFL++ dari: {plot_file}")
    with open(plot_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 7:
                try:
                    t = clean_num(parts[0]) / 60.0      # Menit
                    c = int(clean_num(parts[3]))        # Corpus count
                    e = clean_num(parts[6])             # Map density / coverage %
                    
                    # Tambahkan data secara atomik agar panjang array selalu sama
                    times.append(t)
                    corpus.append(c)
                    edges.append(e)
                except Exception:
                    continue

if times:
    print(f"[+] Berhasil mengekstrak {len(times)} data points time-series.")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5), dpi=300)

    # Plot 1: Edge Coverage Evolution
    ax1.plot(times, edges, color='#1f77b4', lw=2.2, label='cJSON Map Density (%)')
    ax1.set_title('Branch / Map Coverage Over Time', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Time Elapsed (Minutes)', fontsize=9)
    ax1.set_ylabel('Map Coverage / Density (%)', fontsize=9)
    ax1.legend(loc='lower right')
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Plot 2: Corpus Discovery Growth
    ax2.plot(times, corpus, color='#2ca02c', lw=2.2, label='Grammar-Aware JSON Seeds')
    ax2.set_title('Corpus Exploration & Lineage Growth', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Time Elapsed (Minutes)', fontsize=9)
    ax2.set_ylabel('Corpus Queue Count', fontsize=9)
    ax2.legend(loc='lower right')
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('coverage_benchmark_lab5.png')
    print("[+] Grafik visualisasi berhasil disimpan: coverage_benchmark_lab5.png")
else:
    print("[-] Gagal mem-parsing data dari plot_data.")
