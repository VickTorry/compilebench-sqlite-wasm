# Compile SQLite to WebAssembly

You are given SQLite 3.45.0 source code at `/workdir/sqlite.tar.gz`.
Your goal is to compile it to WebAssembly using Emscripten.

## Requirements

1. Install Emscripten toolchain
2. Extract SQLite source from the tarball
3. Compile SQLite to WebAssembly using Emscripten
4. Place the output files at `/workdir/result/sqlite.wasm` and `/workdir/result/sqlite.js`
5. Verify the compiled WebAssembly module can execute a basic SQL query

## Expected Result

- `/workdir/result/sqlite.wasm` must exist and be a valid WebAssembly binary
- `/workdir/result/sqlite.js` must exist
- Running a basic SQL query through the compiled module must return correct results
