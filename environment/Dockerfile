FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    git \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workdir

# Download SQLite 3.45.0 source
RUN wget -q https://www.sqlite.org/2024/sqlite-autoconf-3450000.tar.gz \
    && mv sqlite-autoconf-3450000.tar.gz sqlite.tar.gz

# Create result directory
RUN mkdir -p /workdir/result