FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
ENV AFL_SKIP_CPUFREQ=1

# Install toolchain and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    llvm \
    llvm-dev \
    git \
    make \
    python3 \
    python3-pip \
    gdb \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pytest z3-solver matplotlib

WORKDIR /fuzzer_workspace
COPY . /fuzzer_workspace

RUN chmod +x ./fuzzer fuzzer_cli.py

# Default execution: run test suite and generate evaluation reports
CMD ["/bin/bash", "-c", "pytest -v tests/ && ./fuzzer benchmark && ./fuzzer report"]
