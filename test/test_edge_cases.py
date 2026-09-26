import pytest
from parse import parser
from lexicals import lexer
from semantics import SemanticAnalyze, SemanticError
from codegen import CodeGenerator

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def assert_semantic_error(code: str, error_substr: str = ""):
    """Parses and runs semantics, asserting SemanticError is raised with optional message matching."""
    ast = parser.parse(code, lexer=lexer)
    sem = SemanticAnalyze()
    with pytest.raises(SemanticError) as exc_info:
        sem.analyse(ast)
    if error_substr:
        assert error_substr.lower() in str(exc_info.value).lower(), (
            f"Expected '{error_substr}' in error message, got: '{exc_info.value}'"
        )

def assert_syntax_error(code: str):
    """Asserts that the parser rejects the code with SyntaxError."""
    with pytest.raises(SyntaxError):
        parser.parse(code, lexer=lexer)

# ==========================================
# 1. SYNTAX & GRAMMAR FAILURE CASES
# ==========================================

def test_syntax_unterminated_string():
    assert_syntax_error('let s: str = "hello world\n')

def test_syntax_double_operator():
    assert_syntax_error('let x: i32 = 1 ++ 2')

def test_syntax_missing_brace():
    assert_syntax_error('proc foo :i32() { let x: i32 = 1')

def test_syntax_invalid_assignment_target():
    assert_syntax_error('10 = 20')

# ==========================================
# 2. TYPE SYSTEM & ASSIGNMENT FAILURES
# ==========================================

def test_type_mismatch_int_to_str():
    assert_semantic_error('let x: i32 = "hello"', "declared 'i32' got 'str'")

def test_type_mismatch_float_to_bool():
    assert_semantic_error('let b: bool = 3.14', "declared 'bool' got 'f32'")

def test_type_mismatch_reassign():
    code = """
    let x: i32 = 10
    x = "string"
    """
    assert_semantic_error(code, "cannot be assigned 'str'")

def test_const_reassignment_rejected():
    code = """
    const i32 MAX_COUNT = 100
    MAX_COUNT = 101
    """
    assert_semantic_error(code, "cannot reassign to const")

def test_undeclared_variable_reassign():
    assert_semantic_error('undeclared_var = 42', "not declared in this scope")

def test_duplicate_variable_same_scope():
    code = """
    let x: i32 = 1
    let x: i32 = 2
    """
    assert_semantic_error(code, "already defined in this scope")

# ==========================================
# 3. CONTROL FLOW & JUMP INVARIANTS
# ==========================================

def test_break_outside_loop():
    assert_semantic_error('let x: i32 = 1\nbreak', "outside of loop")

def test_continue_outside_loop():
    assert_semantic_error('continue', "outside of loop")

def test_return_outside_procedure():
    assert_semantic_error('return 42', "outside of a procedure")

def test_procedure_return_type_mismatch():
    code = """
    proc get_number :i32() {
        return "not an integer"
    }
    """
    assert_semantic_error(code, "expected 'i32' got 'str'")

# ==========================================
# 4. PROCEDURE CALL FAILURES
# ==========================================

def test_call_undefined_procedure():
    assert_semantic_error('let x: i32 = unknown_proc()', "not defined in this scope")

def test_call_argument_count_too_few():
    code = """
    proc add :i32(a: i32, b: i32) {
        return a + b
    }
    let res: i32 = add(1)
    """
    assert_semantic_error(code, "expects 2 arguments, got 1")

def test_call_argument_count_too_many():
    code = """
    proc add :i32(a: i32, b: i32) {
        return a + b
    }
    let res: i32 = add(1, 2, 3)
    """
    assert_semantic_error(code, "expects 2 arguments, got 3")

def test_call_argument_type_mismatch():
    code = """
    proc square :i32(n: i32) {
        return n * n
    }
    let res: i32 = square("hello")
    """
    assert_semantic_error(code, "argument 1 expected 'i32', got 'str'")

# ==========================================
# 5. ARRAY EDGE CASES & BOUNDARY REJECTIONS
# ==========================================

def test_array_size_mismatch_with_literal():
    code = """
    let arr[3]: i32 = [1, 2, 3, 4, 5]
    """
    assert_semantic_error(code, "declared with size 3, got 5 elements")

def test_array_element_type_mismatch():
    code = """
    let arr[3]: i32 = [1, "two", 3]
    """
    assert_semantic_error(code, "must be of type 'i32', got 'str'")

def test_array_indexing_non_array():
    code = """
    let x: i32 = 10
    let y: i32 = x[0]
    """
    assert_semantic_error(code, "index access must be on an array")

def test_array_non_integer_index():
    code = """
    let arr[3]: i32 = [10, 20, 30]
    let y: i32 = arr["first"]
    """
    assert_semantic_error(code, "array index must be an integer")

def test_array_assign_element_type_mismatch():
    code = """
    let arr[3]: i32 = [10, 20, 30]
    arr[0] = "invalid"
    """
    assert_semantic_error(code, "elements must be of type 'i32', got 'str'")

# ==========================================
# 6. END-TO-END PASSING BOUNDARY TESTS
# ==========================================

def test_nested_loops_with_break_and_continue(run_stkt):
    code = """
    let outer_count: i32 = 0
    let i: i32 = 0
    while i < 3 {
        let j: i32 = 0
        while j < 5 {
            if j == 2 {
                break
            }
            j = j + 1
        }
        outer_count = outer_count + 1
        i = i + 1
    }
    onscreen outer_count
    """
    output = run_stkt(code)
    assert "3" in output

def test_operator_precedence(run_stkt):
    code = """
    let a: i32 = 2 + 3 * 4
    let b: i32 = (2 + 3) * 4
    onscreen a
    onscreen b
    """
    output = run_stkt(code)
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    assert "14" in lines
    assert "20" in lines

def test_ternary_expression_evaluation(run_stkt):
    code = """
    let score: i32 = 85
    let grade: str = (score >= 60) ? "PASS" : "FAIL"
    onscreen grade
    """
    output = run_stkt(code)
    assert "PASS" in output

def test_zero_and_negative_array_values(run_stkt):
    code = """
    let numbers[4]: i32 = [0, -10, -20, 30]
    onscreen numbers[0]
    onscreen numbers[1]
    onscreen numbers[1] + numbers[2]
    """
    output = run_stkt(code)
    assert "0" in output
    assert "-10" in output
    assert "-30" in output

def test_if_else_if_ladder(run_stkt):
    code = """
    let score: i32 = 85
    let grade: str = "F"

    if score >= 90 {
        grade = "A"
    } else if score >= 80 {
        grade = "B"
    } else if score >= 70 {
        grade = "C"
    } else {
        grade = "F"
    }

    onscreen grade
    """
    output = run_stkt(code)
    assert "B" in output

def test_lambda_execution(run_stkt):
    code = """
    let mult = L :i32(x: i32) {
        return x * 3
    }
    let add = L :i32(a: i32, b: i32) {
        return a + b
    }
    onscreen mult(10)
    onscreen add(7, 8)
    """
    output = run_stkt(code)
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    assert "30" in lines
    assert "15" in lines

def test_onkey_input_execution(run_stkt):
    code = """
    let val: i32 = onkey: i32
    onscreen val * 2
    """
    output = run_stkt(code, user_input="21\n")
    assert "42" in output

def test_match_case_execution(run_stkt):
    code = """
    let code: i32 = 404
    match code {
        case 200 { onscreen "OK" }
        case 404 { onscreen "NOT FOUND" }
        case _   { onscreen "DEFAULT" }
    }
    let fallback: i32 = 999
    match fallback {
        case 100 { onscreen "ONE" }
        case _   { onscreen "FALLBACK" }
    }
    """
    output = run_stkt(code)
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    assert "NOT FOUND" in lines
    assert "FALLBACK" in lines

# ==========================================
# 11. DYNAMIC ARRAYS / SLICES TESTS
# ==========================================

def test_slice_append_and_len(run_stkt):
    code = """
    let arr: [i32] = [1, 2]
    append(arr, 3)
    append(arr, 4)
    onscreen len(arr)
    """
    output = run_stkt(code)
    assert "4" in output

def test_slice_pop_execution(run_stkt):
    code = """
    let arr: [i32] = [10, 20, 30]
    let removed: i32 = pop(arr)
    onscreen removed
    onscreen len(arr)
    """
    output = run_stkt(code)
    assert "30" in output
    assert "2" in output

def test_slice_indexing_and_reassignment(run_stkt):
    code = """
    let arr: [i32] = [5, 10, 15]
    arr[1] = 99
    onscreen arr[1]
    """
    output = run_stkt(code)
    assert "99" in output

def test_slice_type_mismatch_rejection():
    code = """
    let arr: [i32] = [1, 2]
    append(arr, "invalid_string")
    """
    assert_semantic_error(code, "cannot append 'str' to slice of type '[i32]'")

def test_export(run_stkt):
    code="""
    """

# ==========================================
# 12. SYNC & EXPORT MODULE TESTS
# ==========================================

def test_sync_module_public_procedure(tmp_path, run_stkt):
    mod_file = tmp_path / "math_mod.stkt"
    mod_file.write_text("""
    export proc add :i32(a: i32, b: i32) {
        return a + b
    }
    """)
    main_code = f"""
    sync "{str(mod_file)}"
    let sum: i32 = add(10, 20)
    onscreen sum
    """
    output = run_stkt(main_code)
    assert "30" in output

def test_sync_module_private_procedure_rejected(tmp_path):
    mod_file = tmp_path / "priv_mod.stkt"
    mod_file.write_text("""
    proc secret :i32() {
        return 42
    }
    """)
    main_code = f"""
    sync "{str(mod_file)}"
    let v: i32 = secret()
    """
    assert_semantic_error(main_code, "not defined in this scope")

def test_sync_nonexistent_module_rejected():
    code = """
    sync "/path/that/does/not/exist.stkt"
    """
    assert_semantic_error(code, "does not exist")
