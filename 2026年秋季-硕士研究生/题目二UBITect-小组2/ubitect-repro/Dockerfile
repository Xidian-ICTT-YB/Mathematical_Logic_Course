# UBITect backlog.c tutorial build environment.
# Target platform is deliberately linux/amd64: the pinned LLVM 7 binaries are
# x86_64 Linux executables and the author's KLEE is built against them.
FROM --platform=linux/amd64 ubuntu:24.04

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        bc \
        build-essential \
        ca-certificates \
        curl \
        file \
        gdb \
        git \
        jq \
        less \
        libbz2-dev \
        libcap-dev \
        libedit-dev \
        libffi-dev \
        liblzma-dev \
        libncurses-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        patch \
        procps \
        psmisc \
        python3 \
        python3-minimal \
        rsync \
        time \
        unzip \
        xz-utils \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Official prebuilt LLVM/clang 7.0.0, pinned by SHA256 in the host script.
COPY downloads/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz /tmp/llvm7.tar.xz
RUN mkdir -p /opt/llvm7 \
    && tar -xJf /tmp/llvm7.tar.xz --strip-components=1 -C /opt/llvm7 \
    && rm -f /tmp/llvm7.tar.xz \
    && test "$(/opt/llvm7/bin/llvm-config --version)" = "7.0.0" \
    && test "$(/opt/llvm7/bin/llvm-config --has-rtti)" = "NO"

# Pinned uv (Linux x86_64).  Python itself is installed into the bind-mounted
# project so host and container never share an interpreter or virtualenv.
COPY downloads/uv-x86_64-unknown-linux-gnu-0.13.6.tar.gz /tmp/uv.tar.gz
RUN tar -xzf /tmp/uv.tar.gz -C /tmp \
    && install -m 0755 /tmp/uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv \
    && rm -rf /tmp/uv.tar.gz /tmp/uv-x86_64-unknown-linux-gnu \
    && uv --version

ENV PATH="/opt/llvm7/bin:${PATH}" \
    LLVM_DIR="/opt/llvm7/lib/cmake/llvm" \
    LD_LIBRARY_PATH="/opt/llvm7/lib"

WORKDIR /work
CMD ["/bin/bash"]
