#!/bin/bash
set -ex

# Install Emscripten
cd /workdir
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh

# Extract SQLite source
cd /workdir
tar -xzf sqlite.tar.gz
cd sqlite-autoconf-3450000

# Compile SQLite to WebAssembly using Emscripten
emconfigure ./configure
emmake make

# Compile to .wasm and .js output
emcc sqlite3.c \
  -o /workdir/result/sqlite.js \
  -s WASM=1 \
  -s EXPORTED_FUNCTIONS='["_sqlite3_open","_sqlite3_exec","_sqlite3_close"]' \
  -s EXPORTED_RUNTIME_METHODS='["cwrap","ccall"]' \
  -s MODULARIZE=1 \
  -s EXPORT_NAME='sqlite3' \
  -O2

# Verify output exists
ls -la /workdir/result/