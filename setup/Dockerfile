# Multi-language benchmark: C++, Rust, Java, Python

# Stage 1: Builder - compile all compiled-language implementations
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    make \
    pkg-config \
    curl \
    ca-certificates \
    git \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /build

# Build Rust implementation (release)
COPY segtree_rust/ segtree_rust/
RUN cd segtree_rust && cargo build --release

# Build C++ implementation (Makefile -> build/segtree_cpp)
COPY segtree_cpp/ segtree_cpp/
RUN make -C segtree_cpp

# Compile Java classes (build.sh -> .class in segtree_java/)
COPY segtree_java/ segtree_java/
RUN cd segtree_java && sh build.sh

# Stage 2: Runtime - minimal, all language runtimes + Python analysis libs
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-pandas \
    python3-matplotlib \
    python3-seaborn \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PYTHONPATH="/workspace"

WORKDIR /workspace

# Copy project files (build artifacts excluded via .dockerignore)
COPY . /workspace/

# Copy pre-built binaries/classes from builder
COPY --from=builder /build/segtree_rust/target/release/segtree_rust \
    /workspace/segtree_rust/target/release/segtree_rust
COPY --from=builder /build/segtree_cpp/ /workspace/segtree_cpp/
COPY --from=builder /build/segtree_java/ /workspace/segtree_java/
