def test_fibonacci_and_loops(run_stkt):
    code = """
proc fib:i32(n:i32){
    if n <= 1 {
        return n
    } else {
        return fib(n-1) + fib(n-2)
    }
}
let x:i32 = fib(5)
onscreen(x)
    """
    output = run_stkt(code)
    assert "5" in output


def test_function(run_stkt):
    code = """
proc add:i32(a:i32, b:i32){
    return a + b
}

let y :i32 = add(5, 7)
onscreen(y)
    """
    output = run_stkt(code)
    assert "12" in output
