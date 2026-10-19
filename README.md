# Stkt 

## Table of contents
- [General Information](#general-information)
- [key Functions](key-functions)
- [Command and Installation](#command-and-installation)
- [Full Documentation](#full-documentation)

____

### General Information
  Stkt is a statically typed, self-hosted compiled programming language design for clarity, safety and high performance. It features a clean syntax, type inference, fixed-size arrays, hashmap, functions and more.
____
  
### Key Functions
- **Functional Programming**: First-class named functions (`fn`) and anonymous lambdas (`L`), with clean module export (`export fn`) and namespaced imports (`incl "..." as ...`).
- **String Interpolation**: Seamless `{expression}` variable interpolation inside print statements (`onscreen "Hello, {name}!"`) and dynamic string expressions.
- **Standard Library**: Modular built-in libraries with zero external dependencies—including `time`, `os`, `io`, `string`, `math`, `collections`, `algo`, and `json`.
- **Active Error Handling**: Expressive, zero-overhead error propagation without heavy exception tables using `.isok?("panic message")` for assertions and `.or(fallback_val)` for safe defaults.
- **Memory Management**: Dual-tier memory support: stack-allocated fixed strings (`str[N]`) and fast region-based arena allocation (`create_mem`, `mem_reset`, `mem_destroy`) for zero-fragmentation workloads.
- **Built-in Data Structures**: Native dynamic slices (`[T]`), open-chaining hash maps (`hmap[K: V]`), custom compound `struct`/`type`, and standard library collections (`queue`, `stackt`, `set`).


### Command and Installation

#### Fast Installation (Zero-Dependency) 
stat ships with pre-compiled C amalgamation seed (`bootstrap/stkt.c`) requiring zero python or external dependencies :

```bash
# Option 1 : Quick installation script (build and install to ~/.local/bin/stkt)
./install.sh

# Option 2 : Using Makefile
make
make install
```
> [!IMPORTANT]
> Make sure `~/.local/bin` is in your PATH :export PATH="$HOME/.local/bin:$PATH"

#### Full 3-Stage Self-Hosted Boostrap
To verify complete compiler self-hosted from source :

```bash
make bootstrap
```
This runs Stage 1 (Python reference), Stage 2 (Stkt compiled by Stage 1), and Stage 3 (Stkt compiled by Stage 2), verifying bit-for-bit identical convergence (`diff -u build/stage2.c build/stage3.c`).

### CLI Commands
```bash
# 1. Run a .stkt file immediately (compile and execute in sandbox)
stkt run hello.stkt

# short hand
stkt hello.stkt

# 2. Build standalone executable
stkt build hello.stkt -o my_app
./my_app

# 3. View help and compiler options
stkt --help
```
