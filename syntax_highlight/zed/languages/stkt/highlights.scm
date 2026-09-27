; Keywords
[
  "let"
  "const"
  "type"
  "sync"
  "export"
  "as"
  "if"
  "else"
  "while"
  "loop"
  "step"
  "for"
  "match"
  "case"
  "default"
  "return"
  "break"
  "continue"
] @keyword

; Function declarations
[
  "proc"
  "procedure"
  "L"
] @keyword.function

; Built-in functions
[
  "onscreen"
  "onkey"
  "scan"
  "append"
  "len"
  "pop"
] @function.builtin

; Types
[
  "i8"
  "i16"
  "i32"
  "i64"
  "u8"
  "u16"
  "u32"
  "u64"
  "f32"
  "f64"
  "int"
  "float"
  "bool"
  "char"
  "str"
  "void"
] @type

; Constants & Booleans
[
  "true"
  "false"
] @boolean

; Comments
(comment) @comment

; Strings
(string) @string
(escape_sequence) @string.escape

; Numbers
(number) @number

; Identifiers & Function Calls
(call_expression
  function: (identifier) @function)

(identifier) @variable

; Operators
[
  "+"
  "-"
  "*"
  "/"
  "%"
  "=="
  "!="
  "<"
  "<="
  ">"
  ">="
  "&&"
  "||"
  "!"
  "="
  "|>"
] @operator

; Delimiters & Punctuation
[
  ";"
  ":"
  ","
  "."
] @punctuation.delimiter

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket
