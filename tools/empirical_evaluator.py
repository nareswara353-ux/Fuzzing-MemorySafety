#!/usr/bin/env python3
import math
import json

def calculate_vargha_delaney_a12(treatment, control):
    """
    Menghitung Vargha-Delaney A12 effect size.
    A12 > 0.5: Treatment lebih unggul dari Control
    A12 >= 0.71: Large effect size (standar FuzzBench/ICSE/USENIX)
    """
    m = len(treatment)
    n = len(control)
    if m == 0 or n == 0:
        return 0.5

    # Gabungkan dan hitung rank
    all_data = [(val, 'treatment') for val in treatment] + [(val, 'control') for val in control]
    all_data.sort(key=lambda x: x[0])

    rank_sum_treatment = 0
    for idx, item in enumerate(all_data, start=1):
        if item[1] == 'treatment':
            rank_sum_treatment += idx

    # Rumus Standar: A12 = (R1 / m - (m + 1) / 2) / n
    a12 = (rank_sum_treatment / m - (m + 1) / 2.0) / n
    return round(float(a12), 4)

def mann_whitney_u_test(treatment, control):
    """
    Menghitung Mann-Whitney U-statistic dan estimasi p-value 2-tailed (asymptotik).
    """
    m = len(treatment)
    n = len(control)
    if m == 0 or n == 0:
        return 0, 1.0

    all_data = [(val, 'treatment') for val in treatment] + [(val, 'control') for val in control]
    all_data.sort(key=lambda x: x[0])

    r1 = sum(idx for idx, item in enumerate(all_data, start=1) if item[1] == 'treatment')
    u1 = r1 - (m * (m + 1)) / 2.0
    u2 = (m * n) - u1
    u = min(u1, u2)

    # Nilai mean & varians U
    mean_u = (m * n) / 2.0
    sigma_u = math.sqrt((m * n * (m + n + 1)) / 12.0)
    
    if sigma_u == 0:
        return u, 1.0

    z = abs(u - mean_u) / sigma_u
    # Estimasi p-value complementary error function (Normal approx)
    p_value = math.erfc(z / math.sqrt(2))
    return round(float(u), 2), round(float(p_value), 6)

def run_fuzzbench_evaluation(treatment_runs, control_runs):
    a12 = calculate_vargha_delaney_a12(treatment_runs, control_runs)
    u_stat, p_val = mann_whitney_u_test(treatment_runs, control_runs)

    mean_treatment = sum(treatment_runs) / len(treatment_runs) if treatment_runs else 0
    mean_control = sum(control_runs) / len(control_runs) if control_runs else 0

    is_significant = p_val < 0.05
    effect_label = "Negligible"
    if a12 >= 0.71:
        effect_label = "Large Superiority (Significant)"
    elif a12 >= 0.64:
        effect_label = "Medium Superiority"
    elif a12 >= 0.56:
        effect_label = "Small Superiority"

    return {
        "trials_count": len(treatment_runs),
        "treatment_mean": round(mean_treatment, 2),
        "control_mean": round(mean_control, 2),
        "mann_whitney_u": u_stat,
        "p_value": p_val,
        "is_statistically_significant": is_significant,
        "vargha_delaney_a12": a12,
        "effect_size": effect_label
    }

if __name__ == "__main__":
    # Benchmark Sintetik: 10 Trial Branch Coverage (Novel LLVM-AI vs Vanilla AFL)
    novel_ai = [142, 148, 155, 140, 150, 153, 147, 152, 149, 158]
    vanilla_afl = [85, 90, 88, 92, 87, 84, 89, 91, 86, 93]

    res = run_fuzzbench_evaluation(novel_ai, vanilla_afl)
    print(json.dumps(res, indent=2))
