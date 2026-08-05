# Multi-language benchmark: C++, Rust, Java, Python

# Stage 1: Builder - compile the Rust implementation
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    make \
    pkg-config \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Build Rust implementation (release)
WORKDIR /build
COPY segtree_rust/ segtree_rust/
RUN cd segtree_rust && cargo build --release

# Stage 2: Runtime - minimal with all language runtimes
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-pip \
    openjdk-17-jre-headless \
    build-essential \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust from builder
COPY --from=builder /root/.cargo /root/.cargo
COPY --from=builder /root/.rustup /root/.rustup

ENV PATH="/root/.cargo/bin:${PATH}"
ENV RUSTUP_HOME="/root/.rustup"
ENV CARGO_HOME="/root/.cargo"
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PYTHONPATH="/workspace"

WORKDIR /workspace

# Copy project files
COPY . /workspace/

# Copy pre-built Rust binary
COPY --from=builder /build/segtree_rust/target/release/segtree_rust \
    /workspace/segtree_rust/target/release/segtree_rust
