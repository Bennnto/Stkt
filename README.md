# Stkt 

> 📖 **Comprehensive Manual & Story-Driven Guide**: Looking for the full handbook, hands-on tutorial, complete standard library API reference, troubleshooting guide, and performance benchmarks? Read [DOCUMENTATION.md](DOCUMENTATION.md).

## Table of contents
- [General Information](#general-information)
- [Lexicals and Keywords](#lexical-and-keywords)
- [key Function](key-functions)
- [Command and Installation](#command-and-installation)
- [Full Documentation](#full-documentation)

____

### General Information
  Stkt is a statically typed, compiled programming language design for clarity, safety and high performance. It features a clean syntax, type inference, fixed-size arrays, procedures and more compile directly to standard c99 and native machine code using host c toolchains ('clang' or 'gcc').
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
} else if x == 10 {
    x = 0
} else {
    x = x - 1
}

// While loop
while x < 10 {
    x = x + 1
}

// For loop
for let i: i32 = 0; i < 10; i = i + 1 {
    onscreen i
}

// Loop with step
loop 10 step 2 {
    onscreen "Step by 2"
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

#### Match and Case 
```stkt
// Match expression with case statements 
match code {
    case 200 { onscreen "OK" }
    case 404 { onscreen "Not Found" }
    case _   { onscreen "Unknown" }
}
```

#### String 
2 type of string 
  - str in heap unknown size
  - str[n] in stack known size
```stkt
let word: str = "hello"
let word1: str[10] = "hello"
```

____

### Full Documentation

For the comprehensive language reference, visit [DOCUMENTATION.md](DOCUMENTATION.md):
- **Prologue & Core Philosophy**: Why Stkt was built and how C99 emission works
- **Hands-On Tutorial**: 5 progressive steps building up to a native shell (`stkt-sh`)
- **Data Structures**: Fixed arrays, dynamic slices, native hash maps (`hmap`), custom structs
- **Standard Library API**: Exhaustive reference for `io`, `string`, `math`, `collections`, `algo`, `os`, `stackt`, `queue`, `set`
- **Troubleshooting & FAQ**: Common compiler errors, CLI diagnostics, C compiler setup
- **Testing & Debugging**: `--emit-c` inspection, `lldb`/`gdb` workflows, native unit testing
- **Performance**: Binary size benchmarks (~16 KB stripped), sub-second compilation speed, zero-overhead C abstraction
- **Editor Setup**: VS Code TextMate grammar, Neovim/Vim syntax configurations, LSP roadmap
