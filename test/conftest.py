import tempfile
import pytest
import subprocess
from pathlib import Path

from parse import parser
from lexicals import lexer
from semantics import SemanticAnalyze
from codegen import CodeGenerator
from stktc import find_c_compiler

@pytest.fixture
def run_stkt():
    """Fixture that compile and executes stkt source code string and return stdout."""
    def _runner(source_code:str, user_input:str="")->str:
        ast = parser.parse(source_code, lexer=lexer)
        sem = SemanticAnalyze()
        sem.analyse(ast)

        gen = CodeGenerator()
        c_code = gen.generate(ast)

        compiler = find_c_compiler()
        with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as tmp_c:
            tmp_c.write(c_code)
            c_path = Path(tmp_c.name)

        bin_path = c_path.with_suffix(".out")

        try:
            subprocess.run([compiler, "-O2", str(c_path), "-o", str(bin_path)], check=True)
            res = subprocess.run([str(bin_path)], input=user_input, capture_output=True, text=True, check=True)
            return res.stdout
        finally:
            if c_path.exists() : c_path.unlink()
            if bin_path.exists() : bin_path.unlink()

    return _runner
