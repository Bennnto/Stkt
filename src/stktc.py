import argparse
import os
import re
import sys
from pathlib import Path
import shutil
import tempfile
import subprocess

from parse import parser
from semantics import SemanticAnalyze, SemanticError
from codegen import CodeGenerator
from lexicals import lexer

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stkt Language Compiler (targets C99)",
        prog="stktc",
        add_help=True
    )
    parser.add_argument("file", type=Path, help="Path to .stkt source file")
    parser.add_argument("-o", "--output", type=Path, help="Output binary name")
    parser.add_argument("--emit-c", action="store_true", help="Emit generated C code only and exit")
    parser.add_argument("--emit-ast", action="store_true", help="Print parsed AST structure and exit")
    parser.add_argument("--run", action="store_true", help="Run executable file immediately after compilation")
    parser.add_argument("-O", "--opt", default="-O2", choices=["-O0", "-O1", "-O2", "-O3", "-Os"], help="Optimization level")
    parser.add_argument("-cc", "--compiler", type=str, default="auto", help="Specify host C compiler (clang, gcc, or auto)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose compiler output")
    return parser

def find_c_compiler(preferred: str | None = "auto") -> str:
    if preferred and preferred != "auto":
        found = shutil.which(preferred)
        if not found:
            raise RuntimeError(f"Requested C compiler '{preferred}' not found on PATH.")
        return found

    for candidate in ["clang", "gcc", "cc", "cl"]:
        found = shutil.which(candidate)
        if found:
            return found

    raise RuntimeError(
        "No C compiler found on system PATH. Please install clang or gcc."
    )

def print_formatted_error(err_type: str, message: str, filename: str, source_code: str, lineno: int | None = None, token_val: str | None = None):
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    loc_str = f"{filename}:{lineno}" if lineno else filename
    print(f"\n{RED}Error [{err_type}]:{RESET} {BOLD}{message}{RESET}", file=sys.stderr)
    print(f"{BLUE}  --> {loc_str}{RESET}", file=sys.stderr)

    lines = source_code.splitlines()
    if lineno and 1 <= lineno <= len(lines):
        line_content = lines[lineno - 1]
        line_prefix = f" {lineno:3d} | "
        indent_pad = " " * len(line_prefix)
        print(f"{BLUE}{indent_pad}|{RESET}", file=sys.stderr)
        print(f"{BLUE}{line_prefix}{RESET}{line_content}", file=sys.stderr)
        
        # Calculate caret position
        caret_indent = " " * (len(line_content) - len(line_content.lstrip()))
        carets = "^" * max(1, len(token_val) if token_val else len(line_content.strip()))
        print(f"{BLUE}{indent_pad}| {RED}{caret_indent}{carets}{RESET}", file=sys.stderr)
    print(file=sys.stderr)

def compile_stkt(source_path: Path, args: argparse.Namespace) -> int:
    if not source_path.exists():
        print(f"Error: Input file '{source_path}' does not exist.", file=sys.stderr)
        return 2

    source_code = source_path.read_text(encoding="utf-8")

    # 1. Parse
    try:
        ast = parser.parse(source_code, lexer=lexer)
    except SyntaxError as e:
        msg = str(e)
        # Extract line number and token from message if available
        line_match = re.search(r"line (\d+)", msg)
        token_match = re.search(r"token '([^']+)'", msg)
        lineno = int(line_match.group(1)) if line_match else 1
        tok = token_match.group(1) if token_match else None
        
        clean_msg = f"Unexpected token '{tok}'" if tok else msg
        print_formatted_error("SyntaxError", clean_msg, source_path.name, source_code, lineno=lineno, token_val=tok)
        return 1

    if args.emit_ast:
        print(ast)
        return 0

    # 2. Semantic Analysis
    analyzer = SemanticAnalyze()
    try:
        analyzer.analyse(ast)
    except SemanticError as e:
        print_formatted_error("SemanticError", str(e), source_path.name, source_code)
        return 1

    # 3. Generate C code
    generator = CodeGenerator()
    c_code = generator.generate(ast)

    output_bin = args.output or source_path.with_suffix("")
    output_c = output_bin.with_suffix(".c")

    # 4. Handle --emit-c
    if args.emit_c:
        output_c.write_text(c_code, encoding="utf-8")
        if args.verbose:
            print(f"[stktc] Emitted C code: {output_c}")
        return 0

    # 5. Compile C to Native Executable
    compiler = find_c_compiler(args.compiler)
    if args.verbose:
        print(f"[stktc] Using C compiler: {compiler}")

    with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as tmp:
        tmp.write(c_code)
        tmp_c_path = Path(tmp.name)

    try:
        cmd = [compiler, args.opt, "-Wall", "-Wextra", str(tmp_c_path), "-o", str(output_bin)]
        if args.verbose:
            print(f"[stktc] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"C Toolchain Error:\n{result.stderr}", file=sys.stderr)
            return 1
    finally:
        if tmp_c_path.exists():
            tmp_c_path.unlink()

    if args.verbose:
        print(f"[stktc] Built binary: {output_bin}")

    # 6. Execute if --run is specified
    if args.run:
        if args.verbose:
            print(f"[stktc] Running: {output_bin}")
        exec_res = subprocess.run([str(output_bin.resolve())])
        return exec_res.returncode

    return 0

def main():
    parser = create_parser()
    args = parser.parse_args()
    try:
        exit_code = compile_stkt(args.file, args)
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
