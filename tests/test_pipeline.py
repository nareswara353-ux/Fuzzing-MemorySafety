import pytest
import os
import struct
import json
import subprocess
import sys

# Tambahkan root path ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 1. Test Validitas Ekstraksi Constraint LLVM
def test_constraint_format():
    constraints_path = "fuzz_lab4_llvm_pass/extracted_constraints.json"
    if not os.path.exists(constraints_path):
        pytest.skip("File extracted_constraints.json belum digenerate")
    
    with open(constraints_path, "r") as f:
        data = json.load(f)
    
    assert "extracted_integers" in data, "Key 'extracted_integers' tidak ditemukan"
    assert "hex_tokens" in data, "Key 'hex_tokens' tidak ditemukan"
    assert isinstance(data["extracted_integers"], list)
    assert isinstance(data["hex_tokens"], list)

# 2. Test Format Protokol Biner (PACK Header Encoding/Decoding)
def test_packet_encoding_integrity():
    magic = b"PACK"
    version = 0x02
    chunk_count = 1
    payload = b"\x7f\x45" + b"A" * 62
    payload_len = len(payload)

    # Encode header: <4s B H H
    header = struct.pack("<4sBHH", magic, version, chunk_count, payload_len)
    raw_packet = header + payload

    # Verifikasi unpacking
    unpacked_magic, unpacked_ver, unpacked_chunks, unpacked_len = struct.unpack("<4sBHH", raw_packet[:9])
    
    assert unpacked_magic == b"PACK", "Magic bytes corrupt"
    assert unpacked_ver == 2, "Versi protokol salah"
    assert unpacked_chunks == 1, "Chunk count mismatch"
    assert unpacked_len == 64, "Payload length mismatch"
    assert raw_packet[9:11] == b"\x7f\x45", "Payload magic header tidak sesuai"

# 3. Test In-Memory Mutator Fallback Sanity
def test_mutator_fallback_sanity():
    import importlib.util
    mutator_path = "fuzz_lab6_adaptive_stagnation/ai_mutator_adaptive.py"
    
    spec = importlib.util.spec_from_file_location("ai_mutator_adaptive", mutator_path)
    mutator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mutator)
    
    mutator.init(1234)
    original_buf = bytearray(b"PACK\x02\x00\x02\x00\x10\x7f\x45" + b"B" * 14)
    
    mutated = mutator.fuzz(original_buf, None, 1024)
    assert isinstance(mutated, (bytearray, bytes)), "Mutator harus mengembalikan bytearray atau bytes"
    assert len(mutated) > 0, "Mutated buffer tidak boleh kosong"
    mutator.deinit()

# 4. Test Telemetry Dashboard Generator
def test_dashboard_generator():
    from tools.generate_dashboard import scan_all_experiments, generate_html_dashboard
    
    exps = scan_all_experiments()
    assert isinstance(exps, list), "scan_all_experiments harus mengembalikan list"
    
    test_html = "/tmp/test_report.html"
    generate_html_dashboard(exps, output_html=test_html)
    
    assert os.path.exists(test_html), "File HTML dashboard gagal digenerate"
    with open(test_html, "r") as f:
        content = f.read()
    assert "Compiler-Guided Neural Fuzzing" in content, "Judul dashboard tidak ditemukan di HTML"
    os.remove(test_html)

# 5. Test Corpus Minimizer Functionality
def test_corpus_minimizer():
    from tools.corpus_minimizer import minimize_corpus
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
        # Buat seed tiruan (termasuk duplikat)
        for i in range(5):
            with open(os.path.join(tmp_in, f"seed_{i}.bin"), "wb") as f:
                f.write(b"DUPLICATE_DATA_PAYLOAD")
        with open(os.path.join(tmp_in, "unique_seed.bin"), "wb") as f:
            f.write(b"TOTALLY_UNIQUE_PAYLOAD_123")

        orig_cnt, min_cnt, red_pct = minimize_corpus(tmp_in, tmp_out)
        
        assert orig_cnt == 6, "Total file input harus 6"
        assert min_cnt == 2, "Setelah deduplikasi harus tersisa tepat 2 seed unik"
        assert red_pct > 0, "Harus mencatat reduksi persentase ukuran"

# 6. Test Lab 8 Distance Feedback Mutator Sanity
def test_distance_guided_mutator():
    import importlib.util
    mut_path = "fuzz_lab8_branch_distance/ai_mutator_distance.py"
    if not os.path.exists(mut_path):
        pytest.skip("Lab 8 mutator not yet created")

    spec = importlib.util.spec_from_file_location("ai_mutator_distance", mut_path)
    mut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mut)

    mut.init(42)
    sample = bytearray(b"VLLX" + b"\x00" * 12)
    res = mut.fuzz(sample, None, 64)
    assert len(res) >= 16, "Mutated buffer must retain minimum protocol size"
    mut.deinit()

# 7. Test Academic LaTeX Paper Generator
def test_paper_generator():
    from tools.generate_paper_report import collect_experiment_metrics, generate_latex_paper
    import tempfile

    exps = collect_experiment_metrics()
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tf:
        tex_path = tf.name

    generate_latex_paper(exps, output_tex=tex_path)
    assert os.path.exists(tex_path), "File LaTeX gagal digenerate"
    
    with open(tex_path, "r") as f:
        content = f.read()
    assert "\\documentclass[conference]{IEEEtran}" in content, "Format template IEEE LaTeX tidak sesuai"
    assert "Nareswara" in content, "Nama author tidak ditemukan di template"
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
    assert sol is not None, "Z3 Solver harus menemukan solusi satisfiability (SAT)"
    magic, x, y, chk = sol
    assert magic == 0x5a544d53, "Magic header mismatch"
    assert (x ^ y) == 0x5a5a5a5a, "Bitwise XOR constraint violated"
    assert ((x << 3) + (y >> 2)) & 0xFFFFFFFF == 0x1bf754a5, "Bit shift constraint violated"
    assert ((x * 17) + (y * 31)) & 0xFFFFFFFF == chk, "Checksum equation violated"
