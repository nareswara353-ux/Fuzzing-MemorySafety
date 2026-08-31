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

# 19. Test Lab 20 Stateful Protocol Sequence Mutator
def test_stateful_protocol_mutator():
    import importlib.util
    mut_path = "fuzz_lab20_stateful_network/ai_mutator_stateful.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 20 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_stateful", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(123)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 128)

    # Validasi Header Paket Pertama (HELLO -> Type 0x01, Len 4, 'HELO')
    assert res[0] == 0x01, "Message 1 harus bertipe MSG_HELLO"
    assert res[1] == 4
    assert res[2:6] == b"HELO"

    # Validasi Header Paket Kedua (AUTH -> Type 0x02, Len 4, 0x1337C0DE)
    assert res[6] == 0x02, "Message 2 harus bertipe MSG_AUTH"
    assert struct.unpack("<I", res[8:12])[0] == 0x1337C0DE, "Auth token harus valid"
    mut.deinit()

# 20. Test Lab 21 WebAssembly Bytecode Structure Mutator
def test_wasm_bytecode_mutator():
    import importlib.util
    mut_path = "fuzz_lab21_wasm_jit/ai_mutator_wasm.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 21 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_wasm", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(555)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 128)

    # Validasi WASM Header
    assert res[:4] == b"\x00asm", "WASM magic header mismatch"
    assert res[4:8] == b"\x01\x00\x00\x00", "WASM version mismatch"
    # Validasi Type Section ID (0x01)
    assert res[8] == 0x01
    mut.deinit()

# 21. Test Lab 22 Distributed Cloud Fuzzing Coordinator & Mutator
def test_distributed_cluster_engine():
    import importlib.util
    import tempfile
    from fuzz_lab22_distributed_cluster.cluster_sync_engine import DistributedCorpusCoordinator, synthesize_cluster_seed

    with tempfile.TemporaryDirectory() as shared_dir, tempfile.TemporaryDirectory() as worker_in:
        coord = DistributedCorpusCoordinator(shared_pool_dir=shared_dir)
        
        seed_data = synthesize_cluster_seed(1, 100, 0xCC, b"CLUSTER_SYNC_ALL")
        assert len(seed_data) == 74, "Ukuran paket cluster harus 74 bytes"
        
        # Test 1: Broadcast seed baru
        added, path = coord.broadcast_seed(1, seed_data)
        assert added is True
        assert os.path.exists(path)

        # Test 2: Deduplikasi seed kembar
        dup_added, _ = coord.broadcast_seed(2, seed_data)
        assert dup_added is False, "Seed yang identik harus ter-deduplikasi"

        # Test 3: Sinkronisasi ke worker inbox
        synced = coord.sync_worker_inbox(worker_in)
        assert synced == 1, "Harus menyinkronkan 1 seed unik ke antrean worker"

    # Test Mutator
    mut_path = "fuzz_lab22_distributed_cluster/ai_mutator_cluster.py"
    spec = importlib.util.spec_from_file_location("ai_mutator_cluster", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(777)
    res = mut.fuzz(bytearray(b"\x00" * 74), None, 128)
    assert struct.unpack("<I", res[:4])[0] == 0x54534944, "Magic DIST header harus terkunci"
    mut.deinit()

# 22. Test Lab 23 Automated Program Repair & Patch Verification
def test_auto_program_repair():
    from tools.auto_patcher import generate_and_verify_patch

    src = "fuzz_lab23_auto_patching/vuln_target.c"
    poc = "fuzz_lab23_auto_patching/in/crash_poc.bin"
    valid = "fuzz_lab23_auto_patching/in/seed_valid.bin"

    if os.path.exists(src) and os.path.exists(poc) and os.path.exists(valid):
        res = generate_and_verify_patch(src, poc, valid)
        assert res["poc_vulnerability_fixed"] is True, "Patch harus memperbaiki crash PoC"
        assert res["no_regression_confirmed"] is True, "Patch tidak boleh merusak seed valid"
        assert res["patch_file"] is not None
        assert os.path.exists(res["patch_file"])

# 23. Test Lab 24 Java/JVM Execution Harness & Structure Mutator
def test_java_jvm_fuzzing_harness():
    import importlib.util
    import struct
    from fuzz_lab24_java_jvm_harness.java_fuzz_runner import execute_java_target

    # Test Mutator Logic
    mut_path = "fuzz_lab24_java_jvm_harness/ai_mutator_java.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 24 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_java", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4156414A, "Magic JAVA header harus terkunci"
    assert len(res) >= 8
    mut.deinit()

    # Test JVM Execution Runner jika bytecode TargetParser.class ada
    class_dir = "fuzz_lab24_java_jvm_harness"
    crash_file = "fuzz_lab24_java_jvm_harness/in/crash_jvm.bin"
    if os.path.exists(os.path.join(class_dir, "TargetParser.class")) and os.path.exists(crash_file):
        res_exec = execute_java_target(class_dir, "TargetParser", crash_file)
        assert res_exec["crashed"] is True, "Runner harus mendeteksi uncaught JVM exception"

# 24. Test Lab 25 Java Insecure Deserialization Mutator & Oracle
def test_java_deserialization_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab25_java_deserialization.deserial_runner import run_deserialization_test

    # Test Mutator
    mut_path = "fuzz_lab25_java_deserialization/ai_mutator_deserial.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 25 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_deserial", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(99)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 128)

    # Validasi Java Serialization Header (Big-Endian 0xACED 0x0005)
    magic, version, tc_obj, tc_class = struct.unpack(">HHBB", res[:6])
    assert magic == 0xACED, "Stream magic harus 0xACED"
    assert version == 0x0005, "Stream version harus 0x0005"
    assert tc_obj == 0x73, "TC_OBJECT identifier mismatch"
    assert tc_class == 0x72, "TC_CLASSDESC identifier mismatch"
    mut.deinit()

    # Test Execution Runner terhadap InsecureDeserializer
    class_dir = "fuzz_lab25_java_deserialization"
    crash_file = "fuzz_lab25_java_deserialization/in/crash_gadget.bin"
    if os.path.exists(os.path.join(class_dir, "InsecureDeserializer.class")) and os.path.exists(crash_file):
        res_exec = run_deserialization_test(class_dir, crash_file)
        assert res_exec["violation_detected"] is True, "Oracle harus menangkap insecure gadget invocation"

def test_jni_boundary_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab26_jni_boundary.jni_runner import run_jni_target

    mut_path = "fuzz_lab26_jni_boundary/ai_mutator_jni.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 26 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_jni", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(1337)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x494e4a24
    assert len(res) >= 8
    mut.deinit()

    class_dir = "fuzz_lab26_jni_boundary"
    crash_file = "fuzz_lab26_jni_boundary/in/crash_jni.bin"
    has_dylib = os.path.exists(os.path.join(class_dir, "libnative_engine.so")) or os.path.exists(os.path.join(class_dir, "libnative_engine.dylib"))
    if os.path.exists(os.path.join(class_dir, "NativeBridge.class")) and has_dylib and os.path.exists(crash_file):
        res_exec = run_jni_target(class_dir, crash_file)
        assert res_exec["crashed"] is True

def test_java_spel_injection_fuzzing():
    import importlib.util
    from fuzz_lab27_java_spel_ognl.spel_runner import run_spel_target

    mut_path = "fuzz_lab27_java_spel_ognl/ai_mutator_spel.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 27 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_spel", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(2024)
    sample = bytearray(b"#{1+1}")
    res = mut.fuzz(sample, None, 128)

    assert res.startswith(b"#{") or res.startswith(b"${")
    assert res.endswith(b"}")
    mut.deinit()

    class_dir = "fuzz_lab27_java_spel_ognl"
    crash_file = "fuzz_lab27_java_spel_ognl/in/crash_spel.bin"
    if os.path.exists(os.path.join(class_dir, "SpelEvaluator.class")) and os.path.exists(crash_file):
        res_exec = run_spel_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_java_xxe_fuzzing():
    import importlib.util
    from fuzz_lab28_java_xxe_bomb.xxe_runner import run_xxe_target

    mut_path = "fuzz_lab28_java_xxe_bomb/ai_mutator_xxe.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 28 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_xxe", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"<root></root>")
    res = mut.fuzz(sample, None, 512)

    assert b"<?xml" in res or b"<" in res
    mut.deinit()

    class_dir = "fuzz_lab28_java_xxe_bomb"
    crash_file = "fuzz_lab28_java_xxe_bomb/in/crash_xxe.bin"
    if os.path.exists(os.path.join(class_dir, "XxeTargetParser.class")) and os.path.exists(crash_file):
        res_exec = run_xxe_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_java_redos_fuzzing():
    import importlib.util
    from fuzz_lab29_java_redos.redos_runner import run_redos_target

    mut_path = "fuzz_lab29_java_redos/ai_mutator_redos.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 29 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_redos", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(101)
    sample = bytearray(b"admin@example")
    res = mut.fuzz(sample, None, 128)

    assert len(res) > 0
    mut.deinit()

    class_dir = "fuzz_lab29_java_redos"
    crash_file = "fuzz_lab29_java_redos/in/crash_redos.bin"
    if os.path.exists(os.path.join(class_dir, "RedosValidator.class")) and os.path.exists(crash_file):
        res_exec = run_redos_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_java_sql_injection_fuzzing():
    import importlib.util
    from fuzz_lab30_java_sql_injection.sql_runner import run_sql_target

    mut_path = "fuzz_lab30_java_sql_injection/ai_mutator_sql.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 30 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_sql", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(303)
    sample = bytearray(b"guest")
    res = mut.fuzz(sample, None, 128)

    assert len(res) > 0
    mut.deinit()

    class_dir = "fuzz_lab30_java_sql_injection"
    crash_file = "fuzz_lab30_java_sql_injection/in/crash_sql.bin"
    if os.path.exists(os.path.join(class_dir, "SqlTargetRepository.class")) and os.path.exists(crash_file):
        res_exec = run_sql_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_jvm_bytecode_agent_coverage():
    import importlib.util
    import struct
    from fuzz_lab31_jvm_bytecode_agent.coverage_runner import run_agent_target

    mut_path = "fuzz_lab31_jvm_bytecode_agent/ai_mutator_agent.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 31 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_agent", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3131)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x41474e54
    assert len(res) >= 8
    mut.deinit()

    class_dir = "fuzz_lab31_jvm_bytecode_agent"
    crash_file = "fuzz_lab31_jvm_bytecode_agent/in/crash_agent.bin"
    if os.path.exists(os.path.join(class_dir, "TargetApp.class")) and os.path.exists(crash_file):
        res_exec = run_agent_target(class_dir, crash_file)
        assert res_exec["crashed"] is True
        assert res_exec["branches_hit"] > 0

def test_java_concurrency_deadlock_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab32_java_concurrency_deadlock.concurrency_runner import run_concurrency_target

    mut_path = "fuzz_lab32_java_concurrency_deadlock/ai_mutator_concurrency.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 32 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_concurrency", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3232)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x54485244
    assert len(res) >= 8
    mut.deinit()

    class_dir = "fuzz_lab32_java_concurrency_deadlock"
    crash_file = "fuzz_lab32_java_concurrency_deadlock/in/crash_thread.bin"
    if os.path.exists(os.path.join(class_dir, "ConcurrentService.class")) and os.path.exists(crash_file):
        res_exec = run_concurrency_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_java_jwt_crypto_bypass_fuzzing():
    import importlib.util
    from fuzz_lab33_java_jwt_crypto.jwt_runner import run_jwt_target

    mut_path = "fuzz_lab33_java_jwt_crypto/ai_mutator_jwt.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 33 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_jwt", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3333)
    sample = bytearray(b"header.payload.sig")
    res = mut.fuzz(sample, None, 256)

    assert b"." in res
    mut.deinit()

    class_dir = "fuzz_lab33_java_jwt_crypto"
    crash_file = "fuzz_lab33_java_jwt_crypto/in/crash_jwt.bin"
    if os.path.exists(os.path.join(class_dir, "JwtAuthService.class")) and os.path.exists(crash_file):
        res_exec = run_jwt_target(class_dir, crash_file)
        assert res_exec["violation_detected"] is True

def test_java_json_differential_fuzzing():
    import importlib.util
    from fuzz_lab34_java_json_diff.diff_json_runner import run_json_diff_target

    mut_path = "fuzz_lab34_java_json_diff/ai_mutator_json.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 34 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_json", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3434)
    sample = bytearray(b'{"user":"test"}')
    res = mut.fuzz(sample, None, 128)

    assert len(res) > 0
    assert b"{" in res and b"}" in res
    mut.deinit()

    class_dir = "fuzz_lab34_java_json_diff"
    crash_file = "fuzz_lab34_java_json_diff/in/crash_diff.bin"
    if os.path.exists(os.path.join(class_dir, "JsonDifferentialOracle.class")) and os.path.exists(crash_file):
        res_exec = run_json_diff_target(class_dir, crash_file)
        assert res_exec["discrepancy_detected"] is True

def test_java_auto_program_repair():
    from tools.java_auto_patcher import patch_and_verify_java

    src = "fuzz_lab35_java_auto_patching/VulnArrayHandler.java"
    crash = "fuzz_lab35_java_auto_patching/in/crash_poc.bin"
    seed = "fuzz_lab35_java_auto_patching/in/seed_valid.bin"

    if os.path.exists(src) and os.path.exists(crash) and os.path.exists(seed):
        res = patch_and_verify_java(src, crash, seed)
        assert res["crash_fixed"] is True
        assert res["no_regression"] is True
        assert res["patch_file"] is not None
        assert os.path.exists(res["patch_file"])

def test_rust_memory_safety_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab36_rust_memory_safety.rust_runner import run_rust_target

    mut_path = "fuzz_lab36_rust_memory_safety/ai_mutator_rust.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 36 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_rust", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3636)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x54535552
    assert len(res) >= 7
    mut.deinit()

    bin_path = "fuzz_lab36_rust_memory_safety/target_rust_bin"
    crash_file = "fuzz_lab36_rust_memory_safety/in/crash_rust.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_rust_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_integer_overflow_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab37_rust_integer_overflow.overflow_runner import run_overflow_target

    mut_path = "fuzz_lab37_rust_integer_overflow/ai_mutator_overflow.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 37 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_overflow", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3737)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4F56464C
    assert len(res) >= 11
    mut.deinit()

    bin_path = "fuzz_lab37_rust_integer_overflow/arithmetic_target_bin"
    crash_file = "fuzz_lab37_rust_integer_overflow/in/crash_overflow.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_overflow_target(bin_path, crash_file)
        assert res_exec["panicked"] is True

def test_rust_ffi_boundary_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab38_rust_ffi_boundary.ffi_runner import run_ffi_target

    mut_path = "fuzz_lab38_rust_ffi_boundary/ai_mutator_ffi.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 38 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_ffi", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3838)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x46464924
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab38_rust_ffi_boundary/rust_ffi_bin"
    crash_file = "fuzz_lab38_rust_ffi_boundary/in/crash_ffi.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_ffi_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_serde_zerocopy_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab39_rust_serde_zerocopy.zerocopy_runner import run_zerocopy_target

    mut_path = "fuzz_lab39_rust_serde_zerocopy/ai_mutator_zerocopy.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 39 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_zerocopy", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(3939)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x5A435059
    assert len(res) >= 8
    mut.deinit()

    bin_path = "fuzz_lab39_rust_serde_zerocopy/serde_zerocopy_target_bin"
    crash_file = "fuzz_lab39_rust_serde_zerocopy/in/crash_zerocopy.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_zerocopy_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_concurrency_poisoning_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab40_rust_concurrency_poisoning.poison_runner import run_poison_target

    mut_path = "fuzz_lab40_rust_concurrency_poisoning/ai_mutator_poison.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 40 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_poison", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4040)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x504F4953
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab40_rust_concurrency_poisoning/concurrency_target_bin"
    crash_file = "fuzz_lab40_rust_concurrency_poisoning/in/crash_poison.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_poison_target(bin_path, crash_file)
        assert res_exec["panicked"] is True

def test_rust_async_starvation_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab41_rust_async_starvation.async_runner import run_async_target

    mut_path = "fuzz_lab41_rust_async_starvation/ai_mutator_async.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 41 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_async", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4141)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4153594E
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab41_rust_async_starvation/async_target_bin"
    crash_file = "fuzz_lab41_rust_async_starvation/in/crash_async.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_async_target(bin_path, crash_file)
        assert res_exec["violation_detected"] is True

def test_rust_asan_lsan_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab42_rust_asan_lsan.asan_runner import run_asan_target

    mut_path = "fuzz_lab42_rust_asan_lsan/ai_mutator_asan.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 42 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_asan", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4242)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4153414E
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab42_rust_asan_lsan/asan_target_bin"
    crash_file = "fuzz_lab42_rust_asan_lsan/in/crash_asan.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_asan_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_macro_ast_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab43_rust_macro_ast.macro_runner import run_macro_target

    mut_path = "fuzz_lab43_rust_macro_ast/ai_mutator_macro.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 43 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_macro", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4343)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4D414352
    assert len(res) >= 6
    mut.deinit()

    bin_path = "fuzz_lab43_rust_macro_ast/macro_target_bin"
    crash_file = "fuzz_lab43_rust_macro_ast/in/crash_macro.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_macro_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_crypto_timing_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab44_rust_crypto_timing.crypto_runner import run_crypto_target

    mut_path = "fuzz_lab44_rust_crypto_timing/ai_mutator_crypto.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 44 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_crypto", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4444)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x43525950
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab44_rust_crypto_timing/crypto_target_bin"
    crash_file = "fuzz_lab44_rust_crypto_timing/in/crash_crypto.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_crypto_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_rust_auto_program_repair():
    from tools.rust_auto_patcher import patch_and_verify_rust

    src = "fuzz_lab45_rust_auto_patcher/vuln_target.rs"
    crash = "fuzz_lab45_rust_auto_patcher/in/crash_poc.bin"
    seed = "fuzz_lab45_rust_auto_patcher/in/seed_valid.bin"

    if os.path.exists(src) and os.path.exists(crash) and os.path.exists(seed):
        res = patch_and_verify_rust(src, crash, seed)
        assert res["crash_fixed"] is True
        assert res["no_regression"] is True
        assert res["patch_file"] is not None
        assert os.path.exists(res["patch_file"])

def test_golang_native_engine_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab46_golang_native_engine.go_runner import run_go_target

    mut_path = "fuzz_lab46_golang_native_engine/ai_mutator_go.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 46 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_go", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4646)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x474F4C47
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab46_golang_native_engine/target_go_bin"
    crash_file = "fuzz_lab46_golang_native_engine/in/crash_go.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_go_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_goroutine_race_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab47_golang_goroutine_race.race_runner import run_race_target

    mut_path = "fuzz_lab47_golang_goroutine_race/ai_mutator_race.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 47 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_race", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4747)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x52414345
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab47_golang_goroutine_race/target_race_bin"
    crash_file = "fuzz_lab47_golang_goroutine_race/in/crash_race.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_race_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_nil_deref_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab48_golang_nil_deref.nil_runner import run_nil_target

    mut_path = "fuzz_lab48_golang_nil_deref/ai_mutator_nil.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 48 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_nil", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4848)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4E494C50
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab48_golang_nil_deref/target_nil_bin"
    crash_file = "fuzz_lab48_golang_nil_deref/in/crash_nil.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_nil_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_cgo_memory_safety_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab49_golang_cgo_memory_safety.cgo_runner import run_cgo_target

    mut_path = "fuzz_lab49_golang_cgo_memory_safety/ai_mutator_cgo.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 49 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_cgo", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(4949)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x43474F21
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab49_golang_cgo_memory_safety/target_cgo_bin"
    crash_file = "fuzz_lab49_golang_cgo_memory_safety/in/crash_cgo.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_cgo_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_unsafe_pointer_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab50_golang_unsafe_slice_header.unsafe_runner import run_unsafe_target

    mut_path = "fuzz_lab50_golang_unsafe_slice_header/ai_mutator_unsafe.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 50 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_unsafe", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5050)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x554E5346
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab50_golang_unsafe_slice_header/target_unsafe_bin"
    crash_file = "fuzz_lab50_golang_unsafe_slice_header/in/crash_unsafe.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_unsafe_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_http_smuggling_fuzzing():
    import importlib.util
    from fuzz_lab51_golang_http_smuggling.http_runner import run_http_target

    mut_path = "fuzz_lab51_golang_http_smuggling/ai_mutator_http.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 51 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_http", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5151)
    sample = bytearray(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    res = mut.fuzz(sample, None, 512)

    assert b"HTTP/1.1" in res
    mut.deinit()

    bin_path = "fuzz_lab51_golang_http_smuggling/target_http_bin"
    crash_file = "fuzz_lab51_golang_http_smuggling/in/crash_http.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_http_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_grpc_protobuf_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab52_golang_grpc_protobuf.grpc_runner import run_grpc_target

    mut_path = "fuzz_lab52_golang_grpc_protobuf/ai_mutator_protobuf.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 52 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_protobuf", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5252)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert len(res) >= 9
    mut.deinit()

    bin_path = "fuzz_lab52_golang_grpc_protobuf/target_grpc_bin"
    crash_file = "fuzz_lab52_golang_grpc_protobuf/in/crash_grpc.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_grpc_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_msan_uninit_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab53_golang_msan_uninit.msan_runner import run_msan_target

    mut_path = "fuzz_lab53_golang_msan_uninit/ai_mutator_msan.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 53 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_msan", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5353)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4D53414E
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab53_golang_msan_uninit/target_msan_bin"
    crash_file = "fuzz_lab53_golang_msan_uninit/in/crash_msan.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_msan_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_ast_reflection_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab54_golang_ast_reflection.reflection_runner import run_reflection_target

    mut_path = "fuzz_lab54_golang_ast_reflection/ai_mutator_reflection.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 54 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_reflection", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5454)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x5245464C
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab54_golang_ast_reflection/target_refl_bin"
    crash_file = "fuzz_lab54_golang_ast_reflection/in/crash_refl.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_reflection_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_crypto_subtle_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab55_golang_crypto_subtle.crypto_runner import run_crypto_target

    mut_path = "fuzz_lab55_golang_crypto_subtle/ai_mutator_crypto_go.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 55 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_crypto_go", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5555)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x474F5342
    assert len(res) >= 5
    mut.deinit()

    bin_path = "fuzz_lab55_golang_crypto_subtle/target_crypto_bin"
    crash_file = "fuzz_lab55_golang_crypto_subtle/in/crash_crypto.bin"
    if os.path.exists(bin_path) and os.path.exists(crash_file):
        res_exec = run_crypto_target(bin_path, crash_file)
        assert res_exec["crashed"] is True

def test_golang_auto_program_repair():
    from tools.go_auto_patcher import patch_and_verify_go

    src = "fuzz_lab56_golang_auto_patcher/vuln_target.go"
    crash = "fuzz_lab56_golang_auto_patcher/in/crash_poc.bin"
    seed = "fuzz_lab56_golang_auto_patcher/in/seed_valid.bin"

    if os.path.exists(src) and os.path.exists(crash) and os.path.exists(seed):
        res = patch_and_verify_go(src, crash, seed)
        assert res["crash_fixed"] is True
        assert res["no_regression"] is True
        assert res["patch_file"] is not None
        assert os.path.exists(res["patch_file"])

def test_nodejs_prototype_pollution_fuzzing():
    import importlib.util
    import json
    from fuzz_lab57_nodejs_prototype_pollution.js_runner import run_js_target

    mut_path = "fuzz_lab57_nodejs_prototype_pollution/ai_mutator_pollution.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 57 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_pollution", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5757)
    sample = bytearray(b"{}")
    res = mut.fuzz(sample, None, 256)

    parsed = json.loads(res.decode("utf-8"))
    assert isinstance(parsed, dict)
    mut.deinit()

    target_js = "fuzz_lab57_nodejs_prototype_pollution/target.js"
    crash_file = "fuzz_lab57_nodejs_prototype_pollution/in/crash_pollution.json"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_js_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_eventloop_redos_fuzzing():
    import importlib.util
    from fuzz_lab58_nodejs_eventloop_redos.eventloop_runner import run_eventloop_target

    mut_path = "fuzz_lab58_nodejs_eventloop_redos/ai_mutator_redos.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 58 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_redos", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5858)
    sample = bytearray(b"aaaa")
    res = mut.fuzz(sample, None, 64)

    assert len(res) > 0
    mut.deinit()

    target_js = "fuzz_lab58_nodejs_eventloop_redos/target.js"
    crash_file = "fuzz_lab58_nodejs_eventloop_redos/in/crash_redos.txt"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_eventloop_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_worker_threads_race_fuzzing():
    import importlib.util
    import json
    from fuzz_lab59_nodejs_worker_threads_race.worker_runner import run_worker_target

    mut_path = "fuzz_lab59_nodejs_worker_threads_race/ai_mutator_worker.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 59 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_worker", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(5959)
    sample = bytearray(b"{}")
    res = mut.fuzz(sample, None, 256)

    parsed = json.loads(res.decode("utf-8"))
    assert "mode" in parsed
    mut.deinit()

    target_js = "fuzz_lab59_nodejs_worker_threads_race/target.js"
    crash_file = "fuzz_lab59_nodejs_worker_threads_race/in/crash_race.json"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_worker_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_vm_context_escape_fuzzing():
    import importlib.util
    from fuzz_lab60_nodejs_vm_context_escape.vm_runner import run_vm_target

    mut_path = "fuzz_lab60_nodejs_vm_context_escape/ai_mutator_vm.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 60 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_vm", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6060)
    sample = bytearray(b"data.value * 2;")
    res = mut.fuzz(sample, None, 128)

    assert len(res) > 0
    mut.deinit()

    target_js = "fuzz_lab60_nodejs_vm_context_escape/target.js"
    crash_file = "fuzz_lab60_nodejs_vm_context_escape/in/crash_escape.txt"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_vm_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_napi_addon_fuzzing():
    import importlib.util
    from fuzz_lab61_nodejs_napi_addon.napi_runner import run_napi_target

    mut_path = "fuzz_lab61_nodejs_napi_addon/ai_mutator_napi.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 61 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_napi", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6161)
    sample = bytearray(b"SAFE_DATA")
    res = mut.fuzz(sample, None, 64)

    assert len(res) > 0
    mut.deinit()

    target_js = "fuzz_lab61_nodejs_napi_addon/target.js"
    crash_file = "fuzz_lab61_nodejs_napi_addon/in/crash_napi.txt"
    addon_file = "fuzz_lab61_nodejs_napi_addon/addon.node"
    if os.path.exists(target_js) and os.path.exists(crash_file) and os.path.exists(addon_file):
        res_exec = run_napi_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_typescript_type_erasure_fuzzing():
    import importlib.util
    import json
    from fuzz_lab62_typescript_type_erasure.ts_runner import run_ts_target

    mut_path = "fuzz_lab62_typescript_type_erasure/ai_mutator_ts_type.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 62 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_ts_type", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6262)
    sample = bytearray(b"{}")
    res = mut.fuzz(sample, None, 256)

    parsed = json.loads(res.decode("utf-8"))
    assert "userId" in parsed
    mut.deinit()

    compiled_js = "fuzz_lab62_typescript_type_erasure/target.js"
    crash_file = "fuzz_lab62_typescript_type_erasure/in/crash_type_confusion.json"
    if os.path.exists(compiled_js) and os.path.exists(crash_file):
        res_exec = run_ts_target(compiled_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_buffer_oob_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab63_nodejs_buffer_oob.buffer_runner import run_buffer_target

    mut_path = "fuzz_lab63_nodejs_buffer_oob/ai_mutator_buffer.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 63 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_buffer", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6363)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x42554646
    assert len(res) >= 9
    mut.deinit()

    target_js = "fuzz_lab63_nodejs_buffer_oob/target.js"
    crash_file = "fuzz_lab63_nodejs_buffer_oob/in/crash_buffer.bin"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_buffer_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_crypto_timing_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab64_nodejs_crypto_timing.crypto_runner import run_crypto_target

    mut_path = "fuzz_lab64_nodejs_crypto_timing/ai_mutator_crypto_js.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 64 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_crypto_js", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6464)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x4A534352
    assert len(res) >= 5
    mut.deinit()

    target_js = "fuzz_lab64_nodejs_crypto_timing/target.js"
    crash_file = "fuzz_lab64_nodejs_crypto_timing/in/crash_crypto.bin"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_crypto_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_wasm_memory_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab65_nodejs_wasm_memory.wasm_runner import run_wasm_target

    mut_path = "fuzz_lab65_nodejs_wasm_memory/ai_mutator_wasm.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 65 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_wasm", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6565)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x5741534D
    assert len(res) >= 9
    mut.deinit()

    target_js = "fuzz_lab65_nodejs_wasm_memory/target.js"
    crash_file = "fuzz_lab65_nodejs_wasm_memory/in/crash_wasm.bin"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_wasm_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_http2_rapid_reset_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab66_nodejs_http2_rapid_reset.http2_runner import run_http2_target

    mut_path = "fuzz_lab66_nodejs_http2_rapid_reset/ai_mutator_http2.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 66 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_http2", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6666)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x48325354
    assert len(res) >= 8
    mut.deinit()

    target_js = "fuzz_lab66_nodejs_http2_rapid_reset/target.js"
    crash_file = "fuzz_lab66_nodejs_http2_rapid_reset/in/crash_http2.bin"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_http2_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_child_process_injection_fuzzing():
    import importlib.util
    from fuzz_lab67_nodejs_child_process_injection.cmd_runner import run_cmd_target

    mut_path = "fuzz_lab67_nodejs_child_process_injection/ai_mutator_cmd.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 67 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_cmd", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6767)
    sample = bytearray(b"file.txt")
    res = mut.fuzz(sample, None, 64)

    assert len(res) > 0
    mut.deinit()

    target_js = "fuzz_lab67_nodejs_child_process_injection/target.js"
    crash_file = "fuzz_lab67_nodejs_child_process_injection/in/crash_cmd.txt"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_cmd_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_typescript_decorator_di_fuzzing():
    import importlib.util
    import json
    from fuzz_lab68_typescript_decorator_di.di_runner import run_di_target

    mut_path = "fuzz_lab68_typescript_decorator_di/ai_mutator_di.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 68 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_di", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6868)
    sample = bytearray(b"{}")
    res = mut.fuzz(sample, None, 256)

    parsed = json.loads(res.decode("utf-8"))
    assert "serviceToken" in parsed
    mut.deinit()

    compiled_js = "fuzz_lab68_typescript_decorator_di/target.js"
    crash_file = "fuzz_lab68_typescript_decorator_di/in/crash_di.json"
    if os.path.exists(compiled_js) and os.path.exists(crash_file):
        res_exec = run_di_target(compiled_js, crash_file)
        assert res_exec["crashed"] is True

def test_nodejs_stream_backpressure_fuzzing():
    import importlib.util
    import struct
    from fuzz_lab69_nodejs_streams_backpressure.stream_runner import run_stream_target

    mut_path = "fuzz_lab69_nodejs_streams_backpressure/ai_mutator_stream.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 69 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_stream", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(6969)
    sample = bytearray(b"\x00" * 32)
    res = mut.fuzz(sample, None, 64)

    assert struct.unpack("<I", res[:4])[0] == 0x5354524D
    assert len(res) >= 7
    mut.deinit()

    target_js = "fuzz_lab69_nodejs_streams_backpressure/target.js"
    crash_file = "fuzz_lab69_nodejs_streams_backpressure/in/crash_stream.bin"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_stream_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_javascript_regex_lookaround_dos_fuzzing():
    import importlib.util
    from fuzz_lab70_javascript_regex_lookaround_dos.lookaround_runner import run_lookaround_target

    mut_path = "fuzz_lab70_javascript_regex_lookaround_dos/ai_mutator_lookaround.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 70 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_lookaround", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(7070)
    sample = bytearray(b"ValidPass123!")
    res = mut.fuzz(sample, None, 64)

    assert len(res) > 0
    mut.deinit()

    target_js = "fuzz_lab70_javascript_regex_lookaround_dos/target.js"
    crash_file = "fuzz_lab70_javascript_regex_lookaround_dos/in/crash_lookaround.txt"
    if os.path.exists(target_js) and os.path.exists(crash_file):
        res_exec = run_lookaround_target(target_js, crash_file)
        assert res_exec["crashed"] is True

def test_python_cext_buffer_overflow():
    from fuzz_lab71_cpython_c_extension.cext_runner import run_cext_target
    target = "fuzz_lab71_cpython_c_extension/target.py"
    crash = "fuzz_lab71_cpython_c_extension/in/crash_overflow.txt"
    if os.path.exists(target) and os.path.exists(crash):
        res = run_cext_target(target, crash)
        assert res["crashed"] == True

def test_cpython_refcount_uaf_fuzzing():
    import importlib.util
    from fuzz_lab72_cpython_refcount_uaf.refcount_runner import run_refcount_target

    mut_path = "fuzz_lab72_cpython_refcount_uaf/ai_mutator_refcount.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 72 mutator not found")

    spec = importlib.util.spec_from_file_location("ai_mutator_refcount", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(7272)
    sample = bytearray(b"SAFE_DATA")
    res = mut.fuzz(sample, None, 64)

    assert len(res) > 0
    mut.deinit()

    target_py = "fuzz_lab72_cpython_refcount_uaf/target.py"
    crash_file = "fuzz_lab72_cpython_refcount_uaf/in/crash_uaf.txt"
    if os.path.exists(target_py) and os.path.exists(crash_file):
        res_exec = run_refcount_target(target_py, crash_file)
        assert res_exec["crashed"] is True
