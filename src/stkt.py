import argparse
import sys
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional
from lexicals import lexer
from parse import parser
from semantics import SemanticAnalyze, SemanticError
from codegen import CodeGenerator

def main():
    arg_parser = argparse.ArgumentParser(description="Stkt language compiler")
    arg_parser.add_argument("source", help="Source file (.stkt)")
    arg_parser.add_argument("-o", "--output", default="output", help="Output executable name")
    arg_parser.add_argument("-O", "--opt", default="2", choices=["0", "1", "2", "3"], help="Optimization level")
    arg_parser.add_argument("--emit-c", action="store_true", help="Emit C code only, do not compile")
    arg_parser.add_argument("--run", action="store_true", help="Run the compiled binary immediately")
    args = arg_parser.parse_args()

    compile(
        source=args.source,
        output=args.output,
        opt=args.opt,
        emit_c=args.emit_c,
        run=args.run
    )


def format_diagnostic(source_path: str, source_code: str, error_type: str, message: str, lineno: Optional[int], col: Optional[int]) -> str:
    lines = source_code.splitlines()
    if lineno and 0 < lineno <= len(lines):
        line_text = lines[lineno - 1]
        col_idx = col or 1
        pointer = " " * (col_idx - 1) + "^"
        return f"{source_path}:{lineno}:{col_idx}: {error_type}: {message}\n    {line_text}\n    {pointer}"
    return f"{source_path}: {error_type}: {message}"


def format_syntax_error(source_path: str, source_code: str, err: SyntaxError) -> str:
    return format_diagnostic(source_path, source_code, "syntax error", getattr(err, "msg", str(err)), err.lineno, err.offset)


def format_semantic_error(source_path: str, source_code: str, err: SemanticError) -> str:
    return format_diagnostic(source_path, source_code, "semantic error", str(err), getattr(err, "lineno", None), getattr(err, "column", None))


def find_c_compiler() -> str:
    for candidate in ["clang", "gcc", "cc"]:
        path = shutil.which(candidate)
        if path:
            return path
    raise RuntimeError("Stkt error: no C compiler found (clang or gcc)")


def compile(source: str, output: str, opt: str = "2", emit_c: bool = False, run: bool = False):
    source_path = Path(source)
    if not source_path.exists():
        print(f"Stkt error : {source} not found", file=sys.stderr)
        sys.exit(1)

    with open(source_path, "r") as f:
        stkt_code = f.read()

    try:
        ast = parser.parse(stkt_code, lexer=lexer)
        analyzer = SemanticAnalyze()
        analyzer.analyse(ast)
    except SyntaxError as err:
        print(format_syntax_error(source, stkt_code, err), file=sys.stderr)
        sys.exit(1)
    except SemanticError as err:
        print(format_semantic_error(source, stkt_code, err), file=sys.stderr)
        sys.exit(1)

    generator = CodeGenerator()
    c_code = generator.generate(ast)
    c_file = f"{output}.c"

    with open(c_file, "w") as f:
        f.write(c_code)

    if emit_c:
        print(f"C source emitted: {c_file}")
        return

    c_compiler = find_c_compiler()

    compile_cmd = [
        c_compiler,
        f"-O{opt}",
        "-std=c99",
        c_file,
        "-o", output,
        "-lm"
    ]

    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("C compilation error:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)
    finally:
        if not emit_c and os.path.exists(c_file):
            try:
                os.remove(c_file)
            except OSError:
                pass

    if run:
        subprocess.run([f"./{output}"])

if __name__ == "__main__":
    main()
