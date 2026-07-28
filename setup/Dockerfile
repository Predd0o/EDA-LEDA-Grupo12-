FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    pkg-config \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y default stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"
ENV RUSTUP_HOME="/root/.rustup"
ENV CARGO_HOME="/root/.cargo"
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PYTHONPATH="/workspace"

WORKDIR /workspace