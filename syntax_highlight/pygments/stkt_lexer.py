"""
Pygments Lexer for the Stkt programming language.
Can be used with Pygments CLI, Sphinx documentation, MkDocs, or web apps.
"""

from pygments.lexer import RegexLexer, words, bygroups
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
)

class StktLexer(RegexLexer):
    name = 'Stkt'
    aliases = ['stkt']
    filenames = ['*.stkt']
    mimetypes = ['text/x-stkt']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'//.*$', Comment.Single),
            (r'/\*.*?\*/', Comment.Multiline),

            # Keywords
            (words((
                'let', 'const', 'type', 'sync', 'export', 'as',
                'if', 'else', 'while', 'loop', 'step', 'for',
                'match', 'case', 'default', 'return', 'break', 'continue'
            ), suffix=r'\b'), Keyword),

            # Function / Lambda keywords
            (words(('proc', 'procedure', 'L'), suffix=r'\b'), Keyword.Declaration),

            # Built-ins
            (words(('onscreen', 'onkey', 'scan', 'append', 'len', 'pop'), suffix=r'\b'), Name.Builtin),

            # Types
            (words((
                'i8', 'i16', 'i32', 'i64',
                'u8', 'u16', 'u32', 'u64',
                'f32', 'f64', 'int', 'float',
                'bool', 'char', 'str', 'void'
            ), suffix=r'\b'), Keyword.Type),

            # Literals
            (words(('true', 'false'), suffix=r'\b'), Keyword.Constant),
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            (r'0[bB][01]+', Number.Bin),
            (r'[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?', Number.Float),
            (r'[0-9]+', Number.Integer),

            # Strings
            (r'"', String, 'string'),
            (r"'(\\.|[^\\'])'", String.Char),

            # Procedures definitions
            (r'(proc|procedure)(\s+)([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Keyword.Declaration, Text, Name.Function)),

            # Function calls
            (r'([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*\()', Name.Function),

            # Identifiers
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),

            # Operators
            (r'==|!=|<=|>=|<|>|&&|\|\||!|\+|-|\*|/|%|&|\||\^|~|<<|>>|=|\s*\|>\s*', Operator),

            # Punctuation
            (r'[{}()\[\],;:]', Punctuation),
        ],
        'string': [
            (r'[^\\"{]+', String),
            (r'\\.', String.Escape),
            (r'\{', Punctuation, 'interpolation'),
            (r'"', String, '#pop'),
        ],
        'interpolation': [
            (r'\}', Punctuation, '#pop'),
            # Include root tokens recursively inside `{expression}`
            ('root', 'root'),
        ]
    }
