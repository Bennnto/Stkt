# Stkt 

## Table of contents
- [General Information](#general-information)
- [Lexicals and Keywords](#lexical-and-keywords)
- [key Function](key-functions)
- [Command and Installation](#command-and-installation)

____

### General Information
  Stkt is a statically typed, compiled systems programming language design for clarity, safety and high performance. It features a clean syntax, type inference, fixed-size arrays, procedures and more compile directly to standard c99 and native machine code using host c toolchains ('clang' or 'gcc').
____
  

### Language Syntax Guide

#### Variables and Constants

```stkt
// Mutable variable with type annotation
let x: i32 = 42

// Mutable variable with inferred type 
let message = "Hello Stkt!"

// Immuatable variable with constant value
const PI: f32 = 3.1415

```

#### Fixed-Size Arrays 

```stkt
// Declare and initialize an array of 3 integers
let numbers[3]: i32 = [1, 2 ,3]

// Read an element by index 
number_0 = numbers[0] > 1

// Mutate an element
numbers[1] = 10 > [1, 10, 3]
```

#### Loops and Control Flow

```stkt
// Control flow with if/else and if else if 
if x < 10 {
    x = x + 1
} else if x = 0 {
    onscreen(x)
} else {
    x = x - 1
} 

// Loop with while support break and continue 
while x > 0 {
    x = x - 1
    if x >= 10 {
        break;
    }
}

// Loop with for support for with condition and C-style increment
for let i = 0; i < 10; i = i + 1 {
    onscreen(i)
}
```

#### Functions and Lambda Functions
- Function in stkt use keyword `proc` called `procedure` and support return value 
- Lambda function use `L` called `lambda`and support return value 

```stkt
// Procedure proc <name> : <return_type> (parameter)
proc add:i32 (a: i32, b: i32) {
    return a + b
}

// Lambda function L : <return_type> (parameter) 
let mult = L :i32(x: i32) {
    return x * 3
}
```


#### Ternary Operator

```stkt
// Ternary Operator <condition> ? <true statement> : <false statement>

let result:i32 = x > 0 ? x : 0

```


#### Standard Input and Output
- Output using `onscreen` to display text on the screen
- input using `onkey` to read input from the user
```stkt
let val :i32 = onkey :i32
let name:str = onkey("Your name: ", str)

onscreen("Hello World")
```
____


#### MATCH and CASE 
```stkt
// Match expression with case statements 
match code {
    case 200 { onscreen "OK" }
    case 404 { onscreen "Not Found" }
    case _   { onscreen "Unknown" }
}
```
