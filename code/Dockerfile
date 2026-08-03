FROM python:3.10-slim
WORKDIR /app

# ============================================
# STAGE 1: Install system dependencies (CACHED)
# ============================================
RUN apt-get update && apt-get install -y \
    ocaml \
    opam \
    build-essential \
    m4 \
    libgmp-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN opam init --disable-sandboxing -y && \
    opam update && \
    eval $(opam env) && \
    opam install -y dune menhir zarith re dune-build-info && \
    echo "OPAM dependencies installed"

RUN apt-get update && apt-get install -y git && \
    git clone https://bitbucket.org/monpoly/monpoly.git /tmp/monpoly && \
    cd /tmp/monpoly && \
    eval $(opam env) && \
    dune build && \
    cp _build/default/src/main.exe /usr/local/bin/monpoly && \
    cd / && rm -rf /tmp/monpoly && \
    apt-get remove -y git && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    echo "MonPoly built and installed successfully"

ENV PATH="/root/.opam/default/bin:${PATH}"

# === ΕΓΚΑΤΑΣΤΑΣΗ TESSLA ===
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget "https://git.tessla.io/tessla/tessla/builds/artifacts/master/raw/target/scala-3.3.1/tessla-assembly-2.1.0.jar?job=deploy" -O /usr/local/bin/tessla.jar
RUN echo '#!/bin/bash\nexec java -jar /usr/local/bin/tessla.jar "$@"' > /usr/local/bin/tessla && \
    chmod +x /usr/local/bin/tessla

# === ΕΓΚΑΤΑΣΤΑΣΗ RTLOLA ===
RUN apt-get update && apt-get install -y \
    curl \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

RUN cargo install rtlola-cli && \
    echo "RTLola installed successfully"
# ==========================

# ============================================
# STAGE 2: Copy application files (LAST - changes often)
# ============================================
COPY . /app
RUN mkdir -p /shared_data

CMD ["python3"]