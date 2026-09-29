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

def test_sync_auto_resolve_standard_library(run_stkt):
    code = """
    sync "math"
    let m: i32 = max(10, 50)
    let s: i32 = sqrt_int(100)
    let g: i32 = gcd(12, 18)
    onscreen "m={m}, s={s}, g={g}"
    """
    output = run_stkt(code)
    assert "m=50, s=10, g=6" in output

def test_sync_auto_resolve_standard_library(run_stkt):
    code = """
    sync "math"
    let m: i32 = max(10, 50)
    let s: i32 = sqrt_int(100)
    let g: i32 = gcd(12, 18)
    onscreen "m={m}, s={s}, g={g}"
    """
    output = run_stkt(code)
    assert "m=50, s=10, g=6" in output

def test_sync_auto_resolve_standard_library(run_stkt):
    code = """
    sync "math"
    let m: i32 = max(10, 50)
    let s: i32 = sqrt_int(100)
    let g: i32 = gcd(12, 18)
    onscreen "m={m}, s={s}, g={g}"
    """
    output = run_stkt(code)
    assert "m=50, s=10, g=6" in output

def test_sync_collections_standard_library(run_stkt):
    code = """
    sync "collections"
    let list: [i32] = [10, 50, 20, 50, 30]
    let tot: i32 = sum_i32(list)
    let mx: i32 = max_elem(list)
    let mn: i32 = min_elem(list)
    let cnt: i32 = count_elem(list, 50)
    let p1: i32 = index_of(list, 20)
    let p2: i32 = index_of(list, 999)
    let has20: bool = contain_i32(list, 20)
    let has99: bool = contain_i32(list, 99)
    onscreen "tot={tot}, mx={mx}, mn={mn}, cnt={cnt}, p1={p1}, p2={p2}, h1={has20}, h2={has99}"
    """
    output = run_stkt(code)
    assert "tot=160, mx=50, mn=10, cnt=2, p1=2, p2=-1, h1=true, h2=false" in output

def test_sync_algo_full_suite(run_stkt):
    code = """
    sync "algo"
    let list: [i32] = [50, 10, 40, 20, 30]
    sort_i32(list)
    let idx30: i32 = binary_search(list, 30)
    let idx99: i32 = binary_search(list, 99)
    reverse_i32(list)
    let first: i32 = list[0]
    let last: i32 = list[4]
    onscreen "idx30={idx30}, idx99={idx99}, first={first}, last={last}"
    """
    output = run_stkt(code)
    assert "idx30=2, idx99=-1, first=50, last=10" in output

def test_sync_string_standard_library(run_stkt):
    code = """
    sync "string"
    let d1: bool = is_digit('7')
    let d2: bool = is_digit('x')
    let up: char = to_upper('m')
    let low: char = to_lower('R')
    let n: i32 = digit_to_int('8')
    let c: char = int_to_digit(3)
    onscreen "d1={d1}, d2={d2}, up={up}, low={low}, n={n}, c={c}"
    """
    output = run_stkt(code)
    assert "d1=true, d2=false, up=M, low=r, n=8, c=3" in output

def test_sync_string_search_and_equality(run_stkt):
    code = """
    sync "string"
    let word: str = "banana"
    let has_n: bool = str_contains(word, 'n')
    let pos_a: i32 = str_index_of(word, 'a')
    let cnt_a: i32 = str_count(word, 'a')
    let w1: str = "apple"
    let w2: str = "apple"
    let w3: str = "orange"
    let same: bool = (w1 == w2)
    let diff: bool = (w1 != w3)
    onscreen "has_n={has_n}, pos_a={pos_a}, cnt_a={cnt_a}, same={same}, diff={diff}"
    """
    output = run_stkt(code)
    assert "has_n=true, pos_a=1, cnt_a=3, same=true, diff=true" in output

def test_sync_namespaced_imports_full(run_stkt):
    code = """
    sync "math" as m
    sync "string" as s
    let sq: i32 = m.sqrt_int(144)
    let p: bool = m.is_prime(17)
    let up: char = s.to_upper('w')
    let d: bool = s.is_digit('8')
    onscreen "sq={sq}, p={p}, up={up}, d={d}"
    """
    output = run_stkt(code)
    assert "sq=12, p=true, up=W, d=true" in output

def test_sync_namespaced_unknown_procedure_rejected():
    code = """
    sync "math" as m
    let bad: i32 = m.unknown_func(10)
    """
    assert_semantic_error(code, "Function 'unknown_func' not found in namespace 'm'")

def test_sync_io_file_operations(run_stkt):
    code = """
    sync "io" as io
    let path: str = "/tmp/stkt_pytest_file.txt"
    let w_ok: bool = io.write_text(path, "Stkt persistent data!")
    let ex: bool = io.file_exists(path)
    let txt: str = io.read_text(path)
    onscreen "w={w_ok}, ex={ex}, txt={txt}"
    """
    output = run_stkt(code)
    import os
    if os.path.exists("/tmp/stkt_pytest_file.txt"):
        os.remove("/tmp/stkt_pytest_file.txt")
    assert "w=true, ex=true, txt=Stkt persistent data!" in output

def test_sync_io_append_and_file_size(run_stkt):
    code = """
    sync "io" as io
    let path: str = "/tmp/stkt_pytest_append.txt"
    let w1: bool = io.write_text(path, "Line1\\n")
    let s1: i32 = io.file_size(path)
    let w2: bool = io.append_text(path, "Line2\\n")
    let s2: i32 = io.file_size(path)
    let txt: str = io.read_text(path)
    onscreen "s1={s1}, s2={s2}, txt={txt}"
    """
    output = run_stkt(code)
    import os
    if os.path.exists("/tmp/stkt_pytest_append.txt"):
        os.remove("/tmp/stkt_pytest_append.txt")
    assert "s1=6, s2=12" in output
    assert "Line1\nLine2" in output

def test_sync_stack_data_structure(run_stkt):
    code = """
    sync "stackt" as st
    let my_stack: [i32] = []
    let e1: bool = st.stack_is_empty(my_stack)
    st.stack_push(my_stack, 100)
    st.stack_push(my_stack, 200)
    st.stack_push(my_stack, 300)
    let peek1: i32 = st.stack_peek(my_stack)
    let pop1: i32 = st.stack_pop(my_stack)
    let pop2: i32 = st.stack_pop(my_stack)
    let peek2: i32 = st.stack_peek(my_stack)
    let pop3: i32 = st.stack_pop(my_stack)
    let e2: bool = st.stack_is_empty(my_stack)
    onscreen "e1={e1}, peek1={peek1}, pop1={pop1}, pop2={pop2}, peek2={peek2}, pop3={pop3}, e2={e2}"
    """
    output = run_stkt(code)
    assert "e1=true, peek1=300, pop1=300, pop2=200, peek2=100, pop3=100, e2=true" in output

def test_sync_queue_data_structure(run_stkt):
    code = """
    sync "queue" as q
    let my_queue: [i32] = []
    let e1: bool = q.queue_is_empty(my_queue)
    q.queue_enqueue(my_queue, 10)
    q.queue_enqueue(my_queue, 20)
    q.queue_enqueue(my_queue, 30)
    let f1: i32 = q.queue_front(my_queue)
    let d1: i32 = q.queue_dequeue(my_queue)
    let f2: i32 = q.queue_front(my_queue)
    let d2: i32 = q.queue_dequeue(my_queue)
    let d3: i32 = q.queue_dequeue(my_queue)
    let e2: bool = q.queue_is_empty(my_queue)
    onscreen "e1={e1}, f1={f1}, d1={d1}, f2={f2}, d2={d2}, d3={d3}, e2={e2}"
    """
    output = run_stkt(code)
    assert "e1=true, f1=10, d1=10, f2=20, d2=20, d3=30, e2=true" in output

def test_sync_string_is_palindrome(run_stkt):
    code = """
    sync "string" as s
    let p1: bool = s.is_palindrome("racecar")
    let p2: bool = s.is_palindrome("noon")
    let p3: bool = s.is_palindrome("hello")
    let p4: bool = s.is_palindrome("z")
    onscreen "p1={p1}, p2={p2}, p3={p3}, p4={p4}"
    """
    output = run_stkt(code)
    assert "p1=true, p2=true, p3=false, p4=true" in output

def test_sync_string_parse_int(run_stkt):
    code = """
    sync "string" as s
    let n1: i32 = s.parse_int("123")
    let n2: i32 = s.parse_int("-456")
    let n3: i32 = s.parse_int("0")
    let n4: i32 = s.parse_int("98765")
    let sum: i32 = n1 + n2
    onscreen "n1={n1}, n2={n2}, n3={n3}, n4={n4}, sum={sum}"
    """
    output = run_stkt(code)
    assert "n1=123, n2=-456, n3=0, n4=98765, sum=-333" in output

def test_sync_os_cli_arguments(run_stkt):
    code = """
    sync "os" as os
    let count: i32 = os.arg_count()
    let args: [str] = os.get_args()
    onscreen "count={count}"
    """
    output = run_stkt(code)
    assert "count=1" in output

def test_sync_string_int_to_str(run_stkt):
    code = """
    sync "string" as s
    let s1: str = s.int_to_str(425)
    let s2: str = s.int_to_str(-108)
    let s3: str = s.int_to_str(0)
    let s4: str = s.int_to_str(7)
    onscreen "s1={s1}, s2={s2}, s3={s3}, s4={s4}"
    """
    output = run_stkt(code)
    assert "s1=425, s2=-108, s3=0, s4=7" in output

def test_isok_success_and_failure(run_stkt):
    # Success case
    code_ok = """
    sync "string" as s
    let res: i32 = s.parse_int("123").isok?("Cannot Parse This Value")
    onscreen "res={res}"
    """
    output = run_stkt(code_ok)
    assert "res=123" in output

    # Failure case exits with non-zero code and prints custom error
    import sys, subprocess, os
    from parse import parser
    from lexicals import lexer
    from semantics import SemanticAnalyze
    from codegen import CodeGenerator

    code_err = """
    sync "string" as s
    let res: i32 = s.parse_int("bad123").isok?("Cannot Parse This Value")
    """
    ast = parser.parse(code_err, lexer=lexer)
    sem = SemanticAnalyze()
    sem.analyse(ast)
    cg = CodeGenerator()
    c_code = cg.generate(ast)
    with open("/tmp/t_test_err.c", "w") as f:
        f.write(c_code)
    subprocess.run(["gcc", "-o", "/tmp/t_test_err", "/tmp/t_test_err.c"])
    run_res = subprocess.run(["/tmp/t_test_err"], capture_output=True, text=True)
    assert run_res.returncode != 0
    assert "Cannot Parse This Value" in run_res.stderr
    for p in ["/tmp/t_test_err.c", "/tmp/t_test_err"]:
        if os.path.exists(p): os.remove(p)

def test_or_fallback_evaluation(run_stkt):
    code = """
    sync "string" as s
    let ok_val: i32 = s.parse_int("3000").or(8080)
    let fallback_val: i32 = s.parse_int("bad_input").or(8080)
    onscreen "ok={ok_val}, fallback={fallback_val}"
    """
    output = run_stkt(code)
    assert "ok=3000, fallback=8080" in output

def test_or_type_mismatch_rejected():
    from parse import parser
    from lexicals import lexer
    from semantics import SemanticAnalyze, SemanticError
    import pytest

    code = """
    sync "string" as s
    let port: i32 = s.parse_int("invalid").or("string_mismatch")
    """
    ast = parser.parse(code, lexer=lexer)
    sem = SemanticAnalyze()
    with pytest.raises(SemanticError):
        sem.analyse(ast)

def test_sync_set_data_structure(run_stkt):
    code = """
    sync "set" as set
    let my_set: [i32] = []
    let a1: bool = set.set_add(my_set, 10)
    let a2: bool = set.set_add(my_set, 20)
    let a3: bool = set.set_add(my_set, 10)
    let sz1: i32 = set.set_size(my_set)
    let has20: bool = set.set_contains(my_set, 20)
    let r20: bool = set.set_remove(my_set, 20)
    let sz2: i32 = set.set_size(my_set)
    let has20_after: bool = set.set_contains(my_set, 20)
    onscreen "a1={a1}, a2={a2}, a3={a3}, sz1={sz1}"
    onscreen "r20={r20}, sz2={sz2}, has20_after={has20_after}"
    """
    output = run_stkt(code)
    assert "a1=true, a2=true, a3=false, sz1=2" in output
    assert "r20=true, sz2=1, has20_after=false" in output

def test_fixed_stack_string_execution(run_stkt):
    code = """
    let greeting: str[16] = "hello"
    greeting[0] = 'H'
    greeting[4] = 'O'
    let c: char = greeting[1]
    onscreen "{greeting}, char={c}"
    """
    output = run_stkt(code)
    assert "HellO, char=e" in output

def test_fixed_stack_string_capacity_overflow():
    import pytest
    from parse import parser
    from lexicals import lexer
    from semantics import SemanticAnalyze, SemanticError

    code = """
    let s: str[3] = "hello"
    """
    ast = parser.parse(code, lexer=lexer)
    sem = SemanticAnalyze()
    with pytest.raises(SemanticError) as exc_info:
        sem.analyse(ast)
    assert "exceeds fixed capacity" in str(exc_info.value)

def test_procedure_taking_and_mutating_fixed_str(run_stkt):
    code = """
    proc set_char: void(buf: str[8], idx: i32, ch: char) {
        buf[idx] = ch
    }

    let message: str[8] = "apple"
    set_char(message, 0, 'A')
    set_char(message, 4, 'Y')
    onscreen "Result: {message}"
    """
    output = run_stkt(code)
    assert "Result: ApplY" in output

def test_string_concatenation_and_slicing(run_stkt):
    code = """
    let hello: str = "Hello "
    let world: str = "World!"
    let greeting: str = hello + world

    let full: str = "A" + "B" + "C" + "D"

    let message: str = "Antigravity Stkt Compiler"
    let w1: str = message[0..11]
    let w2: str = message[12..16]
    let w3: str = message[17..25]

    let stack_s: str[10] = "abcdef"
    let sub_s: str = stack_s[2..5]

    onscreen "{greeting}, {full}, {w1}-{w2}-{w3}, sub={sub_s}"
    """
    output = run_stkt(code)
    assert "Hello World!, ABCD, Antigravity-Stkt-Compiler, sub=cde" in output
