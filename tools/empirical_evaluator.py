#!/usr/bin/env python3
import math
import json

def calculate_vargha_delaney_a12(treatment, control):
    """
    Menghitung Vargha-Delaney A12 effect size via exact pairwise evaluation.
    A12 = 0.5: Identik (No effect)
    A12 > 0.5: Treatment lebih unggul dari Control
    A12 >= 0.71: Large effect size (Standar Google FuzzBench / USENIX Security)
    """
    m = len(treatment)
    n = len(control)
    if m == 0 or n == 0:
        return 0.5

    score = 0.0
    for x in treatment:
        for y in control:
            if x > y:
                score += 1.0
            elif x == y:
                score += 0.5

    a12 = score / (m * n)
    return round(float(a12), 4)

def mann_whitney_u_test(treatment, control):
    """
    Menghitung Mann-Whitney U-statistic dan estimasi p-value 2-tailed (asymptotik).
    """
    m = len(treatment)
    n = len(control)
    if m == 0 or n == 0:
        return 0, 1.0

    score = 0.0
    for x in treatment:
        for y in control:
            if x > y:
                score += 1.0
            elif x == y:
                score += 0.5

    u1 = score
    u2 = (m * n) - u1
    u = min(u1, u2)

    mean_u = (m * n) / 2.0
    sigma_u = math.sqrt((m * n * (m + n + 1)) / 12.0)
    
    if sigma_u == 0:
        return u, 1.0

    z = abs(u - mean_u) / sigma_u
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
    novel_ai = [142, 148, 155, 140, 150, 153, 147, 152, 149, 158]
    vanilla_afl = [85, 90, 88, 92, 87, 84, 89, 91, 86, 93]

    res = run_fuzzbench_evaluation(novel_ai, vanilla_afl)
    print(json.dumps(res, indent=2))
