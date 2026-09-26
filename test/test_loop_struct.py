import pytest
from parse import parser
from lexicals import lexer
from semantics import SemanticAnalyze, SemanticError

def assert_semantic_error(code: str, error_substr: str = ""):
    ast = parser.parse(code, lexer=lexer)
    sem = SemanticAnalyze()
    with pytest.raises(SemanticError) as exc_info:
        sem.analyse(ast)
    if error_substr:
        assert error_substr.lower() in str(exc_info.value).lower(), (
            f"Expected '{error_substr}' in error message, got: '{exc_info.value}'"
        )

# ==========================================
# 1. LOOP TESTS & EDGE CASES
# ==========================================

def test_loop_simple_execution(run_stkt):
    code = """
    let count: i32 = 0
    loop 5 {
        count = count + 1
    }
    onscreen count
    """
    output = run_stkt(code)
    assert "5" in output

def test_loop_with_step(run_stkt):
    code = """
    let total: i32 = 0
    loop 10 step 2 {
        total = total + 1
    }
    onscreen total
    """
    output = run_stkt(code)
    assert "5" in output

def test_nested_loops_independence(run_stkt):
    code = """
    let hits: i32 = 0
    loop 3 {
        loop 4 {
            hits = hits + 1
        }
    }
    onscreen hits
    """
    output = run_stkt(code)
    assert "12" in output

def test_loop_with_break_and_continue(run_stkt):
    code = """
    let sum: i32 = 0
    let counter: i32 = 0
    loop 10 {
        counter = counter + 1
        if counter == 3 {
            continue
        }
        if counter > 5 {
            break
        }
        sum = sum + counter
    }
    onscreen sum
    """
    # 1 + 2 + (skip 3) + 4 + 5 = 12
    output = run_stkt(code)
    assert "12" in output

def test_loop_time_type_must_be_integer():
    code = """
    loop "five" {
        onscreen "invalid"
    }
    """
    assert_semantic_error(code, "loop time type must be an interger type")

def test_loop_step_type_must_be_integer():
    code = """
    loop 10 step 2.5 {
        onscreen "invalid"
    }
    """
    assert_semantic_error(code, "loop step type must be an interger type")

def test_loop_time_smaller_than_step():
    code = """
    loop 2 step 5 {
        onscreen "invalid"
    }
    """
    assert_semantic_error(code, "greater than or equal to the step value")

# ==========================================
# 2. STRUCT / TYPE TESTS & EDGE CASES
# ==========================================

def test_struct_duplicate_type_declaration():
    code = """
    type Point {
        x: i32,
        y: i32
    }
    type Point {
        x: i32,
        y: i32
    }
    """
    assert_semantic_error(code, "already declared")

def test_struct_duplicate_field_declaration():
    code = """
    type Player {
        hp: i32,
        hp: i32
    }
    """
    assert_semantic_error(code, "Field 'hp' declared multiple times in struct 'Player'")

def test_struct_access_undefined_field():
    code = """
    type Point {
        x: i32,
        y: i32
    }
    let p: Point = Point(1, 2)
    onscreen p.z
    """
    # Asserts that accessing an unlisted member fails
    assert_semantic_error(code, "has no field 'z'")
