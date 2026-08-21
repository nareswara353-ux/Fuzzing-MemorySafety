# Compiler-Guided Neural Fuzzing Architecture

> **An End-to-End Hybrid Fuzzing Framework Combining LLVM IR Static Analysis, Local Large Language Models (LLMs), and AFL++ / AddressSanitizer.**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![AFL++](https://img.shields.io/badge/Fuzzer-AFL%2B%2B_v5.03a-red)
![LLVM](https://img.shields.io/badge/Compiler-LLVM_Clang_18+-green)
![LLM Backend](https://img.shields.io/badge/LLM-Qwen2.5--Coder--7B-purple)
![Sanitizer](https://img.shields.io/badge/Sanitizer-AddressSanitizer-orange)
![Build Status](https://github.com/narezzzs/Master-PhD-Project/actions/workflows/ci.yml/badge.svg)


---

## Project Overview

Modern automated vulnerability discovery faces a fundamental trade-off: **fuzzing throughput** (thousands of executions/second) vs. **semantic awareness** (passing complex input grammars and multi-byte magic assertions). Traditional random mutators (Havoc) struggle with deep nested branches and magic headers, while symbolic execution suffers from path explosion.

This project implements a **closed-loop compiler-guided neural fuzzing architecture** that resolves this bottleneck:

1. **Static Compiler Analysis (LLVM IR Pass):** Extracts comparison predicates (`ICmpInst`), boundary integer thresholds, and string/magic constants from target bitcode without manual reverse engineering.
2. **Asynchronous Neural Mutator (LLM Bridge Daemon):** Formulates compiler-extracted constraints into dynamic structured prompts for local LLMs (`Qwen2.5-Coder:7B`), generating semantically valid seeds and boundary exploit candidates.
3. **Decoupled High-Throughput IPC:** Implements an asynchronous producer-consumer bridge via Unix Domain Sockets (`AF_UNIX`), decoupling LLM inference latency (~500ms) from AFL++ raw execution loop (~200–1,000 exec/sec).
4. **Hardware-Assisted Triage:** Integrates AddressSanitizer (ASan) to catch subtle heap memory corruptions and out-of-bounds writes.

---

## System Architecture

```
+-----------------------------------------------------------------------------+
|                                TARGET SOURCE                                |
|                        (target.c / cJSON Parser)                            |
+-----------------------------------------------------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |      LLVM IR Bitcode (.bc)        |
                     +-----------------------------------+
                                       |
                                       v
             +---------------------------------------------------+
             |    Standalone LLVM IR Constraint Extractor        |
             |       - ICmpInst Predicates & Constants           |
             |       - Magic Bytes & String Literals             |
             +---------------------------------------------------+
                                       |
                                       v
                       [ extracted_constraints.json ]
                                       |
                                       v
             +---------------------------------------------------+
             |       Asynchronous Neural Daemon (Python)         |
             |       - Local Model: Qwen2.5-Coder:7B             |
             |       - Dynamic Semantic Prompt Construction      |
             |       - Non-blocking In-Memory Seed Pool          |
             +---------------------------------------------------+
                                       |
                         (Unix Domain Socket: IPC)
                                       v
             +---------------------------------------------------+
             |       AFL++ Custom Python Mutator Engine          |
             |       (ai_mutator.py: init / fuzz / deinit)       |
             +---------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                         AFL++ INSTRUMENTED RUNTIME                          |
|                       (AddressSanitizer Redzones)                           |
+-----------------------------------------------------------------------------+
      |                                                             |
      v                                                             v
[ New Edge / Coverage Map ]                              [ ASan Crash Triage ]
  - Corpus Queue Lineage                                   - Heap Buffer Overflow
  - Bitmap Map Density                                     - Stack Unwinding / Root Cause
```

---

## Laboratory Breakdown (Lab 1 – Lab 5)

| Lab Module | Core Technical Focus | Key Engineering Artifacts | Experimental Outcome |
|---|---|---|---|
| **Lab 1: Baseline Fuzzing** | AFL++ environment configuration, build isolation, AddressSanitizer setup | target.c, AFL++ Clang pipeline | Established baseline execution loop and ASan interceptor |
| **Lab 2: In-Process Mutator** | Binary structure-aware mutation using AFL++ Python Custom Mutator API | ai_mutator.py (init/fuzz/deinit) | Structured packet construction passing magic header verification |
| **Lab 3: Asynchronous IPC Bridge** | Multi-tier architecture decoupling LLM inference overhead from fuzzing execution | llm_daemon.py, Unix Domain Socket (AF_UNIX) | Prevented AFL++ starvation; maintained high execution throughput |
| **Lab 4: LLVM IR Analysis** | Static compilation analysis via custom C++ LLVM Pass to extract comparison constraints | constraint_extractor.cpp, extracted_constraints.json | Automated constraint extraction; triggered heap overflow exploit triage (6,267 crashes) |
| **Lab 5: Real-World Benchmark** | Generalization evaluation against production C parser (cJSON) | fuzz_cjson.c, Grammar-Aware Mutator | Discovered 56 unique syntax-edge testcases; reached 16.50% map density |

---

## Empirical Evaluation & Results

### 1. Exploitation on Binary Target (Lab 4)

- **Vulnerability:** Heap Buffer Overflow (memcpy of size 64 into a 16-byte allocated heap buffer)
- **ASan Detection:** Intercepted write out-of-bounds at address 0x7c0a161e0020 in thread T0 (target.c:33)
- **Efficiency:** Unique exploit payload synthesized and verified within 13 executions (execs: 13, op: ai_mutator)

### 2. Coverage & Corpus Evolution on cJSON (Lab 5)

Benchmarked over a 50-minute continuous fuzzing campaign on cJSON:

- **Corpus Growth:** Expanded from 2 initial seeds to 58 unique lineage testcases (56 discovered via neural grammar mutation)
- **Coverage:** Achieved 16.50% bitmap map density with 27 unique newly explored branch edges

---

## Quickstart & Reproduction

### Prerequisites

- Linux (x86_64)
- LLVM/Clang 18+
- AFL++ v5.03a+
- Python 3.10+
- Ollama running locally with qwen2.5-coder:7b

```bash
ollama run qwen2.5-coder:7b
```

### Running Lab 5 (cJSON Benchmark)

```bash
# 1. Navigate to Lab 5
cd fuzz_lab5_realworld_cjson

# 2. Extract LLVM constraints
clang -O1 -emit-llvm -c cJSON.c -o cjson.bc
./constraint_extractor cjson.bc

# 3. Compile target harness with ASan
AFL_USE_ASAN=1 afl-clang-fast -g -O1 fuzz_cjson.c cJSON.c -o cjson_fuzz

# 4. Terminal 1: Start LLM Daemon
export LLM_MODEL="qwen2.5-coder:7b"
python3 llm_daemon.py

# 5. Terminal 2: Start AFL++ Fuzzing
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
export AFL_SKIP_CPUFREQ=1
export PYTHONPATH="$(pwd)"
export AFL_PYTHON_MODULE=ai_mutator
export AFL_CUSTOM_MUTATOR_ONLY=1

afl-fuzz -i in -o out_cjson -m none -- ./cjson_fuzz @@
```

---

## Research Contributions & Potential

- **Zero-Annotation Invariant Extraction:** Fully automated constraint discovery from LLVM IR, eliminating the need for manual fuzzing dictionary construction.
- **Hybrid Mutation Synthesis:** Resolves the grammar barrier for text-based parsers without sacrificing CPU fuzzing velocity.
- **Academic Foundation:** Serves as the experimental prototype for graduate research in Automated Software Security, Compiler-Guided Vulnerability Synthesis, and AI-Augmented Testing.

---

## Author & Project Info

- **Author:** Radhitya Putra Nareswara
- **Project:** Master / Ph.D. Research Track — Software & Systems Security

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
