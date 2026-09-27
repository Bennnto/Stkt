#!/usr/bin/env python3
"""
Stkt Terminal Syntax Highlighter
A standalone CLI tool to display beautifully colorized .stkt source code in terminal.
Usage:
    python highlight.py path/to/file.stkt
"""

import sys
import re

# ANSI Color codes
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RED = "\033[31m"
GRAY = "\033[90m"

KEYWORDS = {
    "let", "const", "type", "sync", "export", "as",
    "if", "else", "while", "loop", "step", "for",
    "match", "case", "default", "return", "break", "continue"
}

DECLARATIONS = {"proc", "procedure", "L"}

TYPES = {
    "i8", "i16", "i32", "i64",
    "u8", "u16", "u32", "u64",
    "f32", "f64", "int", "float",
    "bool", "char", "str", "void"
}

BUILTINS = {"onscreen", "onkey", "scan", "append", "len", "pop"}
CONSTANTS = {"true", "false"}

TOKEN_REGEX = re.compile(
    r'(?P<COMMENT>//.*?$)|'
    r'(?P<STRING>"(?:\\.|[^"\\])*")|'
    r'(?P<CHAR>\'(\\.|[^\'\\])\')|'
    r'(?P<NUMBER>\b\d+(?:\.\d+)?\b)|'
    r'(?P<IDENT>[a-zA-Z_]\w*)|'
    r'(?P<OPERATOR>==|!=|<=|>=|&&|\|\||\|>|[+\-*/%!=<>&|^~])|'
    r'(?P<PUNCT>[{}()\[\],;:])|'
    r'(?P<WHITESPACE>\s+)|'
    r'(?P<OTHER>.)',
    re.MULTILINE
)

def highlight(code: str) -> str:
    out = []
    for match in TOKEN_REGEX.finditer(code):
        kind = match.lastgroup
        text = match.group()

        if kind == "COMMENT":
            out.append(f"{GRAY}{text}{RESET}")
        elif kind == "STRING":
            # Highlight embedded interpolation {expr}
            parts = re.split(r'(\{.*?\})', text)
            highlighted_str = []
            for p in parts:
                if p.startswith('{') and p.endswith('}'):
                    inner = highlight(p[1:-1])
                    highlighted_str.append(f"{YELLOW}{{{RESET}{inner}{YELLOW}}}{RESET}")
                else:
                    highlighted_str.append(f"{GREEN}{p}{RESET}")
            out.append("".join(highlighted_str))
        elif kind == "CHAR":
            out.append(f"{GREEN}{text}{RESET}")
        elif kind == "NUMBER":
            out.append(f"{CYAN}{text}{RESET}")
        elif kind == "IDENT":
            if text in KEYWORDS:
                out.append(f"{MAGENTA}{BOLD}{text}{RESET}")
            elif text in DECLARATIONS:
                out.append(f"{BLUE}{BOLD}{text}{RESET}")
            elif text in TYPES:
                out.append(f"{CYAN}{BOLD}{text}{RESET}")
            elif text in BUILTINS:
                out.append(f"{YELLOW}{text}{RESET}")
            elif text in CONSTANTS:
                out.append(f"{CYAN}{BOLD}{text}{RESET}")
            else:
                out.append(f"{RESET}{text}{RESET}")
        elif kind == "OPERATOR":
            out.append(f"{RED}{text}{RESET}")
        elif kind == "PUNCT":
            out.append(f"{YELLOW}{text}{RESET}")
        else:
            out.append(text)
    return "".join(out)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        demo = """// Stkt Syntax Highlighting Demo
sync "math"

export proc compute :i32(x: i32, factor: i32) {
    let arr: [i32] = [10, 20, 30]
    append(arr, x * factor)
    onscreen "Result is: {len(arr)}"
    return arr[3]
}
"""
        print(highlight(demo))
    else:
        with open(sys.argv[1], "r") as f:
            print(highlight(f.read()))
