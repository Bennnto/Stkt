import argparse
from pathlib import Path
import os
import sys
from parse import parser
from semantics import SemanticAnalyze
from codegen import CodeGenerator
from lexicals import lexer
import subprocess
import shutil



def main():
    parser = argparse.ArgumentParser(
        prog = "stkt",
        description = "stkt language compiler driver"
    )
    parser.add_argument("source", help="Path to .stkt source file")
    parser.add_argument("-o", "--output", default="output", help="output binary file name")
    parser.add_argument("--emit-c", action="store_true", help="Emit C source file")
    parser.add_argument("--run", action="store_true", help="Run executable after compilation")
    parser.add_argument("-O", "--opt", choices=["0", "1", "2", "3"], default="2",help="Optimization level")

    args = parser.parse_args()

    compile(
        source = args.source,
        output = args.output,
        opt = args.opt,
        emit_c = args.emit_c,
        run = args.run
    )

def find_c_compiler() -> str:
    for candidate in ["clang", "gcc", "cc"]:
        path = shutil.which(candidate)
        if path:
            return path
    raise RuntimeError("Stkt error: no C compiler found (clang or gcc)")

def compile(source:str, output:str, opt:str="2", emit_c:bool=False, run:bool=False):
    source_path = Path(source)
    if not source_path.exists():
        print(f"Stkt error : {source} not found",file=sys.stderr)
        sys.exit(1)


    with open(source_path, "r",) as f:
        stkt_code = f.read()

    ast = parser.parse(stkt_code, lexer=lexer)
    analyzer = SemanticAnalyze()
    analyzer.analyse(ast)
    generator = CodeGenerator()
    c_code = generator.generate(ast)
    c_file = f"{output}.c"
    with open(c_file, "w") as f:
        f.write(c_code)
    if emit_c:
        print(f"Generated {c_file}")
        return
    compiler = find_c_compiler()
    cmd = [compiler, f"-O{opt}", c_file, "-o", output]
    result =subprocess.run(cmd)
    if result.returncode != 0 :
        print(f"Stkt error: C compilation failed", file=sys.stderr)
        sys.exit(result.returncode)

    if run:
        run_cmd = [f"./{output}"]
        subprocess.run(run_cmd)

if __name__ == "__main__":
    main()
