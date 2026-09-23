import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from parse import parser
from lexicals import lexer
from semantics import SemanticAnalyze
from codegen import CodeGenerator

def _test(code: str):
    ast = parser.parse(code, lexer=lexer)
    analyse = SemanticAnalyze()
    analyse.analyse(ast)
    generator = CodeGenerator()
    c_code = generator.generate(ast)
    print(c_code)

if __name__ == "__main__":
    _test("""
proc add :i32(x :i32, y:i32) {
    x + y
}
    """)