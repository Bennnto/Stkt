import pytest
from parse import parser
from lexicals import lexer
from semantics import SemanticAnalyze, SemanticError

def check_semantic_error(code:str, match_msg: str):
    ast = parser.parse(code, lexer=lexer)
    sem = SemanticAnalyze()
    with pytest.raises(SemanticError, match=match_msg):
        sem.analyse(ast)

def test_reject_type_mismatch():
    check_semantic_error('let x:i32 = "hello"', r"declared 'i32' got 'str'")

def test_reject_break_outside_loop():
    check_semantic_error('let x: i32 = 1\nbreak', r"outside of loop")

def test_reject_const_reassignment():
    check_semantic_error('const i32 X = 5\nX = 10', r"Cannot reassign to const")
