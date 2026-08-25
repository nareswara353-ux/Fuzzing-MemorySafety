import pytest
import os
import struct
import json
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 1. Test Validitas Ekstraksi Constraint LLVM
def test_constraint_format():
    constraints_path = "fuzz_lab4_llvm_pass/extracted_constraints.json"
    if not os.path.exists(constraints_path):
        pytest.skip("File extracted_constraints.json belum digenerate")
    
    with open(constraints_path, "r") as f:
        data = json.load(f)
    
    assert "extracted_integers" in data
    assert "hex_tokens" in data
    assert isinstance(data["extracted_integers"], list)
    assert isinstance(data["hex_tokens"], list)

# 2. Test Format Protokol Biner (PACK Header Encoding/Decoding)
def test_packet_encoding_integrity():
    magic = b"PACK"
    version = 0x02
    chunk_count = 1
    payload = b"\x7f\x45" + b"A" * 62
    payload_len = len(payload)

    header = struct.pack("<4sBHH", magic, version, chunk_count, payload_len)
    raw_packet = header + payload

    unpacked_magic, unpacked_ver, unpacked_chunks, unpacked_len = struct.unpack("<4sBHH", raw_packet[:9])
    
    assert unpacked_magic == b"PACK"
    assert unpacked_ver == 2
    assert unpacked_chunks == 1
    assert unpacked_len == 64

# 3. Test In-Memory Mutator Fallback Sanity
def test_mutator_fallback_sanity():
    import importlib.util
    mutator_path = "fuzz_lab6_adaptive_stagnation/ai_mutator_adaptive.py"
    if not os.path.exists(mutator_path):
        pytest.skip("Lab 6 mutator not found")
        
    spec = importlib.util.spec_from_file_location("ai_mutator_adaptive", mutator_path)
    mutator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mutator)
    
    mutator.init(1234)
    original_buf = bytearray(b"PACK\x02\x00\x02\x00\x10\x7f\x45" + b"B" * 14)
    mutated = mutator.fuzz(original_buf, None, 1024)
    assert isinstance(mutated, (bytearray, bytes))
    assert len(mutated) > 0
    mutator.deinit()

# 4. Test Telemetry Dashboard Generator
def test_dashboard_generator():
    from tools.generate_dashboard import scan_all_experiments, generate_html_dashboard
    
    exps = scan_all_experiments()
    assert isinstance(exps, list)
    
    test_html = "/tmp/test_report.html"
    generate_html_dashboard(exps, output_html=test_html)
    assert os.path.exists(test_html)
    os.remove(test_html)

# 5. Test Corpus Minimizer Functionality
def test_corpus_minimizer():
    from tools.corpus_minimizer import minimize_corpus
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
        for i in range(5):
            with open(os.path.join(tmp_in, f"seed_{i}.bin"), "wb") as f:
                f.write(b"DUPLICATE_DATA_PAYLOAD")
        with open(os.path.join(tmp_in, "unique_seed.bin"), "wb") as f:
            f.write(b"TOTALLY_UNIQUE_PAYLOAD_123")

        orig_cnt, min_cnt, red_pct = minimize_corpus(tmp_in, tmp_out)
        assert orig_cnt == 6
        assert min_cnt == 2
        assert red_pct > 0

# 6. Test Lab 8 Distance Feedback Mutator Sanity
def test_distance_guided_mutator():
    import importlib.util
    mut_path = "fuzz_lab8_branch_distance/ai_mutator_distance.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 8 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_distance", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"VLLX" + b"\x00" * 12)
    res = mut.fuzz(sample, None, 64)
    assert len(res) >= 16
    mut.deinit()

# 7. Test Academic LaTeX Paper Generator
def test_paper_generator():
    from tools.generate_paper_report import collect_experiment_metrics, generate_latex_paper
    import tempfile

    exps = collect_experiment_metrics()
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tf:
        tex_path = tf.name

    generate_latex_paper(exps, output_tex=tex_path)
    assert os.path.exists(tex_path)
    os.remove(tex_path)

# 8. Test Lab 9 SMT Z3 Concolic Solver
def test_concolic_z3_solver():
    import importlib.util
    solver_path = "fuzz_lab9_concolic_z3/concolic_solver.py"
    if not os.path.exists(solver_path):
        pytest.skip("Lab 9 solver not found")

    spec = importlib.util.spec_from_file_location("concolic_solver", solver_path)
    solver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver)

    sol = solver.solve_symbolic_guards()
    assert sol is not None
    magic, x, y, chk = sol
    assert magic == 0x5a544d53
    assert (x ^ y) == 0x5a5a5a5a
    assert (((x << 3) & 0xFFFFFFFF) + (y >> 2)) & 0xFFFFFFFF == 0x1ff87307
    assert ((x * 17) + (y * 31)) & 0xFFFFFFFF == chk

# 9. Test Lab 10 Differential Semantic Fuzzing Oracle
def test_differential_semantic_oracle():
    target_bin = "fuzz_lab10_differential/diff_target_fuzz"
    if not os.path.exists(target_bin):
        pytest.skip("Differential target binary not compiled")

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tf_valid, tempfile.NamedTemporaryFile(delete=False) as tf_anomaly:
        tf_valid.write(b"VAL=456")
        tf_valid.flush()
        
        tf_anomaly.write(b"VAL=0456")
        tf_anomaly.flush()

        res_valid = subprocess.run([target_bin, tf_valid.name], capture_output=True)
        assert res_valid.returncode == 0

        res_anomaly = subprocess.run([target_bin, tf_anomaly.name], capture_output=True)
        assert res_anomaly.returncode != 0

    os.remove(tf_valid.name)
    os.remove(tf_anomaly.name)

# 10. Test Lab 11 Dynamic Taint Analysis Mutator Logic
def test_taint_guided_mutator():
    import importlib.util
    mut_path = "fuzz_lab11_taint_analysis/ai_mutator_taint.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 11 taint mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_taint", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)
    
    assert res[:4] == b"DTA!", "Taint mutator harus mengunci Header DTA!"
    assert res[8:10] == b"AA", "Taint mutator harus mengunci Command AA"
    assert struct.unpack("<I", res[16:20])[0] == 0x1337C0DE, "Taint mutator harus mengunci Target Key"
    mut.deinit()

# 11. Test Lab 12 In-Memory Persistent Mutator Integrity
def test_persistent_mutator():
    import importlib.util
    mut_path = "fuzz_lab12_persistent_mode/ai_mutator_persistent.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 12 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_persistent", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(1337)
    sample = bytearray(b"FAST\x04\x00\x00\x00XXXX")
    res = mut.fuzz(sample, None, 64)

    assert res[:4] == b"FAST", "Persistent mutator harus mempertahankan FAST magic header"
    assert struct.unpack("<I", res[4:8])[0] == 4, "Payload length harus 4 bytes"
    assert len(res) >= 12
    mut.deinit()

# 12. Test Lab 13 Automated Exploitability Analyzer & PoC Generator
def test_exploitability_analyzer():
    from tools.exploit_analyzer import analyze_crash_exploitability
    import tempfile

    target_bin = "fuzz_lab13_exploitability_analyzer/target_vuln_bin"
    if not os.path.exists(target_bin):
        pytest.skip("Lab 13 binary not compiled")

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        # Buat payload pembajakan control-flow
        tf.write(b"PWN!" + b"B" * 32 + b"\x41\x41\x41\x41\x00\x00\x00\x00")
        tf.flush()
        
        result = analyze_crash_exploitability(target_bin, tf.name)
        assert result["severity"] == "CRITICAL", "Tingkat keparahan harus terdeteksi CRITICAL"
        assert "Control-Flow Hijack" in result["verdict"], "Harus mendeteksi Control-Flow Hijack"
        assert os.path.exists(result["poc_script"]), "File Python PoC script harus terbuat"
        
        # Bersihkan file sementara
        if os.path.exists(result["poc_script"]):
            os.remove(result["poc_script"])

    os.remove(tf.name)

# 13. Test Lab 14 Local SLM Grammar Mutator Bridge
def test_slm_mutator_bridge():
    import importlib.util
    mut_path = "fuzz_lab14_slm_mutator/ai_mutator_slm.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 14 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_slm", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(99)
    sample = bytearray(b"<PROMPT_REQ> OP=READ; ROLE=GUEST; AUTH_KEY=0x1337 </PROMPT_REQ>")
    res = mut.fuzz(sample, None, 512)

    assert b"<PROMPT_REQ>" in res, "SLM Mutator harus menjaga struktur XML/Prompt tag"
    assert len(res) > 10
    mut.deinit()

# 14. Test Lab 15 Empirical Statistical Evaluation Engine
def test_empirical_evaluator():
    from tools.empirical_evaluator import run_fuzzbench_evaluation, calculate_vargha_delaney_a12

    treatment = [100, 105, 110, 115, 120]
    control = [50, 55, 60, 65, 70]

    res = run_fuzzbench_evaluation(treatment, control)
    assert res["is_statistically_significant"] is True, "Treatment harus terbukti signifikan"
    assert res["vargha_delaney_a12"] == 1.0, "A12 harus 1.0 untuk populasi dominan mutlak"
    assert res["effect_size"] == "Large Superiority (Significant)"

    # Uji kasus data identik (A12 = 0.5, tidak ada efek)
    identical_a12 = calculate_vargha_delaney_a12([10, 20], [10, 20])
    assert 0.4 <= identical_a12 <= 0.6

# 15. Test Lab 16 End-to-End Orchestrator CLI
def test_fuzzer_cli_orchestrator():
    cli_path = "./fuzzer"
    assert os.path.exists(cli_path), "Wrapper executable ./fuzzer harus ada"

    # Test Help Output
    res_help = subprocess.run([cli_path, "--help"], capture_output=True, text=True)
    assert res_help.returncode == 0
    assert "Compiler-Guided Neural Fuzzing Framework" in res_help.stdout

    # Test Subcommand Dry Run
    res_run = subprocess.run([cli_path, "run", "--mode", "concolic"], capture_output=True, text=True)
    assert res_run.returncode == 0
    assert "CONCOLIC" in res_run.stdout

    # Test Subcommand Benchmark
    res_bench = subprocess.run([cli_path, "benchmark"], capture_output=True, text=True)
    assert res_bench.returncode == 0
    assert "Statistical significance" in res_bench.stdout

# 16. Test Lab 17 Kernel IOCTL Structure Mutator
def test_kernel_ioctl_mutator():
    import importlib.util
    mut_path = "fuzz_lab17_kernel_kcov/ai_mutator_ioctl.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 17 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_ioctl", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(77)
    sample = bytearray(b"\x88\x01\x04\x00" + b"\x00" * 64)
    res = mut.fuzz(sample, None, 128)

    assert len(res) == 68, "Ukuran paket IOCTL harus 68 bytes"
    assert res[0] == 0x88, "Magic Driver harus selalu 0x88"
    assert res[1] in [0x01, 0x02, 0x03], "Command ID harus valid"
    mut.deinit()

# 17. Test Lab 18 QEMU Black-Box Binary Fuzzing Mutator & Runner
def test_blackbox_qemu_mutator_and_runner():
    import importlib.util
    mut_path = "fuzz_lab18_qemu_binary_only/ai_mutator_blackbox.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 18 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_blackbox", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"\x00" * 48)
    res = mut.fuzz(sample, None, 64)

    assert res[:4] == b"BIN$", "Black-box mutator harus mengunci Header BIN$"
    assert struct.unpack("<I", res[4:8])[0] == 0x4B4C4142, "Secret Key 0x4B4C4142 harus terkunci"
    mut.deinit()

    # Test Runner
    from fuzz_lab18_qemu_binary_only.qemu_runner import execute_blackbox_target
    target_bin = "fuzz_lab18_qemu_binary_only/target_blackbox_bin"
    crash_file = "fuzz_lab18_qemu_binary_only/in/crash_blackbox.bin"
    if os.path.exists(target_bin) and os.path.exists(crash_file):
        runner_res = execute_blackbox_target(target_bin, crash_file)
        assert runner_res["crashed"] is True, "Target biner tertutup harus terdeteksi crash"

# 18. Test Lab 19 Cross-Architecture Firmware Emulation Mutator & Harness
def test_firmware_emulator_and_mutator():
    import importlib.util
    mut_path = "fuzz_lab19_unicorn_firmware/ai_mutator_firmware.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 19 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_firmware", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(999)
    sample = bytearray(b"\x00" * 75)
    res = mut.fuzz(sample, None, 128)

    assert res[:4] == b"FIRM", "Firmware mutator harus mengunci Header FIRM"
    assert struct.unpack("<I", res[4:8])[0] == 0x00010002, "Device ID 0x00010002 harus terkunci"
    mut.deinit()

    # Test Micro-Emulator Harness
    from fuzz_lab19_unicorn_firmware.firmware_emulator import FirmwareMicroEmulator
    target_bin = "fuzz_lab19_unicorn_firmware/firmware_target_fuzz"
    if os.path.exists(target_bin):
        emu = FirmwareMicroEmulator(target_bin)
        assert emu.read_mmio(0x40000000) == 0x01, "MMIO Status Register harus READY (0x01)"
        
        # Test Payload Overflow Execution
        crash_pkt = struct.pack("<4sIBH64s", b"FIRM", 0x00010002, 0xEE, 32, b"A" * 64)
        run_res = emu.execute_packet(crash_pkt)
        assert run_res["crashed"] is True, "Overflow paket firmware harus memicu crash"
