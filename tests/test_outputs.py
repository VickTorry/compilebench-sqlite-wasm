"""
Tests that verify SQLite has been compiled to WebAssembly correctly.
"""
import os
import subprocess


def run_cmd(cmd, timeout=30):
    """Run command and return result with logging."""
    cmd_str = ' '.join(cmd)
    print(f"\n>>> {cmd_str}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    print(f"[exit={result.returncode}]")
    if result.stdout:
        print(result.stdout[:2000])
    if result.stderr:
        print(f"STDERR: {result.stderr[:1000]}")
    return result


def test_wasm_file_exists():
    """Test that sqlite.wasm exists at /workdir/result/sqlite.wasm."""
    path = "/workdir/result/sqlite.wasm"
    exists = os.path.exists(path)
    print(f"sqlite.wasm exists: {exists}")
    assert exists, "sqlite.wasm should exist at /workdir/result/sqlite.wasm"


def test_js_file_exists():
    """Test that sqlite.js exists at /workdir/result/sqlite.js."""
    path = "/workdir/result/sqlite.js"
    exists = os.path.exists(path)
    print(f"sqlite.js exists: {exists}")
    assert exists, "sqlite.js should exist at /workdir/result/sqlite.js"


def test_wasm_is_not_empty():
    """Test that sqlite.wasm is not an empty or trivially small file."""
    path = "/workdir/result/sqlite.wasm"
    size = os.path.getsize(path)
    print(f"sqlite.wasm size: {size} bytes")
    assert size > 100000, f"sqlite.wasm is too small ({size} bytes) - likely not a real build"


def test_wasm_magic_bytes():
    """
    Test that sqlite.wasm starts with the WebAssembly magic header.
    Every valid .wasm file must start with: 00 61 73 6D
    This catches fake files - AI cannot fake this without actually compiling.
    """
    path = "/workdir/result/sqlite.wasm"
    with open(path, "rb") as f:
        magic = f.read(4)
    print(f"Magic bytes: {magic.hex()}")
    assert magic == b"\x00asm", \
        f"sqlite.wasm does not have valid WebAssembly magic header. Got: {magic.hex()}"


def test_wasm_runs_sql_query():
    """
    Test that the compiled WebAssembly actually executes a real SQL query.
    Uses the low-level C API directly via the exported functions.
    This is the anti-cheat test - the only way to pass is to have a working build.
    """
    test_script = """
const initSqlite = require('/workdir/result/sqlite.js');
initSqlite().then(SQL => {
    // Open an in-memory database via the raw C API
    const filename = SQL.allocate(SQL.intArrayFromString(':memory:'), SQL.ALLOC_NORMAL);
    const ppDb = SQL._malloc(4);
    const openResult = SQL._sqlite3_open(filename, ppDb);
    if (openResult !== 0) {
        console.error('OPEN_FAILED:' + openResult);
        process.exit(1);
    }
    const db = SQL.getValue(ppDb, 'i32');

    // Execute SQL: create table, insert, select
    const sql = SQL.allocate(
        SQL.intArrayFromString(
            "CREATE TABLE t (v TEXT); INSERT INTO t VALUES ('compilebench_proof'); SELECT v FROM t;"
        ),
        SQL.ALLOC_NORMAL
    );

    let resultValue = '';
    const callback = SQL.addFunction((userData, colCount, colValues, colNames) => {
        resultValue = SQL.UTF8ToString(SQL.getValue(colValues, 'i32'));
        return 0;
    }, 'iiiii');

    const execResult = SQL._sqlite3_exec(db, sql, callback, 0, 0);
    SQL._sqlite3_close(db);

    if (execResult !== 0) {
        console.error('EXEC_FAILED:' + execResult);
        process.exit(1);
    }

    if (resultValue === 'compilebench_proof') {
        console.log('SQL_RESULT_OK:' + resultValue);
    } else {
        console.error('SQL_RESULT_WRONG:' + resultValue);
        process.exit(1);
    }
}).catch(err => {
    console.error('WASM_LOAD_ERROR:' + err);
    process.exit(1);
});
"""
    with open("/tmp/run_sqlite_wasm.js", "w") as f:
        f.write(test_script)

    result = run_cmd(["node", "/tmp/run_sqlite_wasm.js"], timeout=60)
    assert result.returncode == 0, f"WASM execution failed:\n{result.stderr}"
    assert "SQL_RESULT_OK:compilebench_proof" in result.stdout, \
        f"SQL query did not return expected result. Got: {result.stdout}"