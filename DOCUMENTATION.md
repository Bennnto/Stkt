# Stkt Language Specification & Reference Manual

Stkt is a statically typed systems programming language that compiles to C99 and native machine code. It provides type inference, dynamic slices, hash maps, arena memory management, pattern matching, and string interpolation without requiring an external runtime or garbage collector.

---

## 1. Compiler Architecture & Pipeline

```
 Source (.stkt)
       │
       ▼
 Lexer / Parser        (AST Construction)
       │
       ▼
 Semantic Analyzer     (Type checking, scope resolution, const checks)
       │
       ▼
 C99 Code Generator    (Emits portable C99 with stkt runtime headers)
       │
       ▼
 Host C Compiler       (clang / gcc with -O3)
       │
       ▼
 Native Executable     (Self-contained ELF / Mach-O binary)
```

The Stkt toolchain is self-hosted. The compiler source lives in `compiler/` and can compile itself. The distribution includes a standalone seed C file (`bootstrap/stkt.c`) so it can be built on any system with a standard C compiler and `make`.

---

## 2. Installation & CLI

### Prerequisites
- POSIX-compliant system (Linux, macOS, BSD)
- C compiler: `clang` or `gcc`
- GNU `make`

### Build from Source

```bash
# Build binary directly from bootstrap seed
make

# Install compiler to ~/.local/bin/stkt
make install

# Optional: verify full 3-stage bootstrap convergence
make bootstrap
```

Ensure `~/.local/bin` is in your `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Command-Line Usage

```bash
# Run a script immediately (compiles to temporary binary and executes)
stkt run main.stkt
stkt main.stkt

# Build a standalone native executable
stkt build main.stkt -o my_binary

# Display help and version
stkt --help
```

---

## 3. Type System & Memory Model

### Primitive Types

| Type | C99 Underlying Type | Size (typical) | Notes |
| :--- | :--- | :--- | :--- |
| `i32` | `int32_t` | 4 bytes | Default signed integer |
| `i64` | `int64_t` | 8 bytes | Timestamps, handles, 64-bit offsets |
| `f32` | `float` | 4 bytes | Single-precision floating point |
| `bool` | `bool` | 1 byte | `true` or `false` |
| `char` | `char` | 1 byte | Single ASCII character literal |
| `str` | `char*` | Pointer | Dynamic null-terminated string |
| `str[N]` | `char[N]` | $N$ bytes | Stack-allocated fixed-capacity string buffer |

### Variable Declarations & Type Inference

```stkt
// Explicit type annotation
let count: i32 = 10
let active: bool = true
let rate: f32 = 1.25

// Type inference
let x = 42             // inferred as i32
let flag = false       // inferred as bool
let name = "stkt"      // inferred as str

// Immutable constants (checked at compile time)
const MAX_LIMIT: i32 = 1024
const PI: f32 = 3.14159
```

### Strings: Dynamic Heap vs Stack Allocation

Stkt provides two string types depending on performance and allocation constraints:

```stkt
// Dynamic string: allocated on heap, can grow
let dynamic_str: str = "allocated on heap"

// Stack string: zero heap allocation, bounded capacity
let fixed_str: str[64] = "bounded stack buffer"

// String interpolation in expressions and print statements
let user: str = "operator"
let id: i32 = 7
onscreen "user={user} id={id}"
```

### Slices (`[T]`)

Dynamic slices are growable lists backed by a dynamically resized heap buffer. Slices track `{ ptr, len, cap }` internally. Passing a slice to a function passes a reference to its header, allowing in-place modifications.

```stkt
// Slice initialization
let items: [i32] = [10, 20, 30]

// Operations
append(items, 40)      // grows buffer if capacity exhausted
let n: i32 = len(items) // 4
let last: i32 = pop(items) // 40

// Indexing and mutation
let first: i32 = items[0]
items[1] = 99
```

### Hash Maps (`hmap[K: V]`)

Stkt features native hash maps with typed keys and values. The runtime implements open-chaining with 64 buckets and FNV-1a hashing.

```stkt
let config: hmap[str: i32] = {}

// Insert / Update
config.set("port", 8080)
config.set("workers", 4)

// Key existence check
if config.has("port") {
    let p: i32 = config.get("port")
    onscreen "Listening on port: {p}"
}

// Iterate over keys
for key in config {
    onscreen "key: {key}"
}
```

### Compound Types (`type`)

Custom structs are defined using `type`:

```stkt
type Header {
    magic: i32,
    length: i32
}

let h: Header
h.magic = 0x5354
h.length = 128

onscreen "magic={h.magic} len={h.length}"
```

---

## 4. Control Flow

### Branching

```stkt
if score >= 90 {
    onscreen "A"
} else if score >= 80 {
    onscreen "B"
} else {
    onscreen "C"
}

// Ternary expression
let status = (code == 200) ? "OK" : "ERROR"
```

### Loops

```stkt
// While loop
let i = 0
while i < 10 {
    i = i + 1
    if i == 3 { continue }
    if i == 8 { break }
}

// For loop
for let idx: i32 = 0; idx < 5; idx = idx + 1 {
    onscreen idx
}

// Stepped iteration
loop 10 step 2 {
    onscreen "step"
}
```

### Pattern Matching

Discrete value matching with default fallback:

```stkt
let exit_code: i32 = 2

match exit_code {
    case 0 { onscreen "success" }
    case 1 { onscreen "general error" }
    case 2 { onscreen "misuse of shell command" }
    case _ { onscreen "unknown exit status" }
}
```

---

## 5. Functions & Lambdas

### Function Signatures

Functions are declared with `fn`, with return type prefixed before the parameter list:

```stkt
fn add: i32(a: i32, b: i32) {
    return a + b
}

fn log_event: void(event: str) {
    onscreen "[LOG] {event}"
}
```

### Lambdas

First-class anonymous functions are declared with `L`:

```stkt
let multiplier = L :i32(val: i32, factor: i32) {
    return val * factor
}

let result = multiplier(6, 7) // 42
```

---

## 6. Error Handling

Stkt uses an active error-flag mechanism rather than heavy C++-style stack unwinding exception tables:
- On failure, operations set an internal error flag `__stkt_has_error = true` and return a zero-value.
- The caller handles errors using `.or()` or asserts with `.isok?()`.

```stkt
incl "string" as s

// Fallback to default value if operation fails
let port: i32 = s.parse_int(user_input).or(8080)

// Assert success; panics and terminates with message if operation fails
let uid: i32 = s.parse_int(id_str).isok?("Invalid numeric user ID")
```

---

## 7. Modules & Namespaces

Modules are organized in individual `.stkt` files. Only functions marked with `export` are accessible externally.

```stkt
// In math/calc.stkt
export fn square: i32(n: i32) {
    return n * n
}

fn internal_helper: void() {
    // private to calc.stkt
}
```

```stkt
// In main.stkt
incl "math/calc.stkt" as calc

let ans = calc.square(9)
```

Standard library modules located in `src/stdlib/` can be included by name without paths:
```stkt
incl "io" as io
incl "os" as os
incl "time" as time
```

---

## 8. Standard Library Reference

### `io` (File Operations)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `file_exists` | `(path: str) -> bool` | Returns `true` if file exists and is accessible. |
| `read_text` | `(path: str) -> str` | Reads entire file into a string. Sets error flag on failure. |
| `write_text` | `(path: str, content: str) -> bool` | Writes string to file, overwriting existing content. |
| `append_text` | `(path: str, content: str) -> bool` | Appends string to file without truncating. |
| `file_size` | `(path: str) -> i32` | Returns file size in bytes, or `-1` if not found. |

```stkt
incl "io" as io

let data = io.read_text("input.txt").or("default")
io.write_text("output.txt", data)
```

### `os` (CLI & System Environment)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `arg_count` | `() -> i32` | Number of CLI arguments (C `argc`). |
| `get_args` | `() -> [str]` | Slice of CLI arguments (index `0` is binary name). |
| `get_env` | `(key: str) -> str` | Reads environment variable, or empty string if unset. |
| `system_cmd` | `(cmd: str) -> i32` | Runs shell command via `system()`. |

```stkt
incl "os" as os

let args = os.get_args()
if os.arg_count() > 1 {
    onscreen "arg1={args[1]}"
}
```

### `string` (String Inspection & Conversion)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `parse_int` | `(s: str) -> i32` | Parses integer from string. Sets error flag on invalid token. |
| `int_to_str` | `(n: i32) -> str` | Converts integer to string. |
| `str_contains` | `(s: str, ch: char) -> bool` | Checks if character occurs in string. |
| `str_index_of` | `(s: str, ch: char) -> i32` | 0-based index of character, or `-1` if absent. |
| `str_count` | `(s: str, ch: char) -> i32` | Count occurrences of character. |
| `is_palindrome` | `(s: str) -> bool` | Bidirectional palindrome check. |
| `to_lower` | `(c: char) -> char` | Converts uppercase ASCII char to lowercase. |
| `to_upper` | `(c: char) -> char` | Converts lowercase ASCII char to uppercase. |
| `is_digit` | `(c: char) -> bool` | Checks if char is between `'0'` and `'9'`. |

### `math` (Arithmetic & Bit Manipulation)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `abs` | `(n: i32) -> i32` | Absolute value. |
| `clamp` | `(v: i32, low: i32, high: i32) -> i32` | Clamps `v` to `[low, high]`. |
| `pow_int` | `(base: i32, exp: i32) -> i32` | Integer exponentiation. |
| `sqrt_int` | `(n: i32) -> i32` | Integer square root using Newton-Raphson. |
| `gcd` | `(a: i32, b: i32) -> i32` | Greatest common divisor. |
| `lcm` | `(a: i32, b: i32) -> i32` | Least common multiple. |
| `is_prime` | `(n: i32) -> bool` | $6k \pm 1$ primality test. |
| `next_prime` | `(n: i32) -> i32` | Smallest prime strictly greater than `n`. |
| `count_ones` | `(n: i32) -> i32` | Bit population count (set bits). |
| `rotate_left` | `(n: i32, shift: i32) -> i32` | Circular bitwise left rotation. |
| `is_power_of_two` | `(n: i32) -> bool` | Verifies power of two. |

### `collections` & `algo` (Slice Operations)

| Function | Module | Signature | Description |
| :--- | :--- | :--- | :--- |
| `sum_i32` | `collections` | `(arr: [i32]) -> i32` | Computes sum of elements. |
| `max_elem` | `collections` | `(arr: [i32]) -> i32` | Maximum element. |
| `min_elem` | `collections` | `(arr: [i32]) -> i32` | Minimum element. |
| `count_elem` | `collections` | `(arr: [i32], val: i32) -> i32` | Count occurrences of `val`. |
| `sort_i32` | `algo` | `(arr: [i32]) -> void` | In-place ascending sort. |
| `binary_search`| `algo` | `(arr: [i32], target: i32) -> i32` | $O(\log N)$ search on sorted slice (-1 if missing). |
| `reverse_i32` | `algo` | `(arr: [i32]) -> void` | In-place slice reversal. |

### `memory` (Arena Bump Allocator)

Arena allocation avoids individual `malloc`/`free` calls by allocating memory sequentially from contiguous chunks.

| Function | Signature | Description |
| :--- | :--- | :--- |
| `create_mem` | `(chunk_size: i32) -> Arena` | Creates an arena with the specified chunk size. |
| `mem_alloc_str`| `(arena: Arena, text: str) -> str` | Allocates and copies a string into the arena. |
| `mem_reset` | `(arena: Arena) -> void` | Resets the bump pointer to zero ($O(1)$ batch free). |
| `mem_destroy` | `(arena: Arena) -> void` | Releases all underlying memory chunks to the OS. |

```stkt
incl "memory" as mem

let arena = mem.create_mem(1024 * 1024) // 1 MB chunk
let s = mem.mem_alloc_str(arena, "temporary string")

// Reset clears all allocations instantly
mem.mem_reset(arena)
mem.mem_destroy(arena)
```

### `time` (POSIX Timing & Sleep)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `now_ms` | `() -> i64` | Epoch timestamp in milliseconds. |
| `now_us` | `() -> i64` | Epoch timestamp in microseconds. |
| `sleep_ms` | `(ms: i32) -> void` | Suspends execution for `ms` milliseconds. |
| `sleep_sec` | `(sec: i32) -> void` | Suspends execution for `sec` seconds. |
| `elapsed_ms`| `(start_ms: i64) -> i64` | Elapsed milliseconds since `start_ms`. |

```stkt
incl "time" as t

let start = t.now_ms()
t.sleep_ms(10)
let elapsed = t.elapsed_ms(start)
```

### `json` (Serialization & Parsing)

| Function | Signature | Description |
| :--- | :--- | :--- |
| `stringify_str` | `(val: str) -> str` | Escapes and wraps string in JSON quotes. |
| `stringify_bool`| `(val: bool) -> str` | Returns `"true"` or `"false"`. |
| `stringify_i32` | `(val: i32) -> str` | Formats integer to string. |
| `stringify_kv` | `(key: str, val_json: str) -> str` | Formats `"key": val_json`. |
| `has_key` | `(json_str: str, key: str) -> bool` | Returns `true` if `key` exists in JSON object. |

---

## 9. Debugging & Tooling

### Native Debugging with LLDB / GDB

Stkt binaries compile with native C symbols, allowing source-level inspection in LLDB or GDB:

```bash
stkt build main.stkt -o app
lldb ./app
(lldb) breakpoint set --name main
(lldb) run
(lldb) register read
```

### Intermediate C99 Inspection

When building or running, the self-hosted compiler emits intermediate C code to `compiler/generated_output.c`. You can inspect this file directly to verify code generation:

```bash
stkt build main.stkt -o app
cat compiler/generated_output.c
```

### VS Code Integration

VS Code configuration is provided under `syntax_highlight/vscode/`:
- Syntax highlighting: `syntax_highlight/vscode/syntaxes/stkt.tmLanguage.json`
- Indentation and brackets: `syntax_highlight/vscode/language-configuration.json`
- Editor settings: `.vscode/settings.json` (4-space indent, auto-indentation)
