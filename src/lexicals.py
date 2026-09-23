import ply.lex as lex

tokens = (
    #---------------------
    # TYPE
    #---------------------
    'STR', 'STR_TYPE',
    'INT', 'INT_TYPE', 'I8', 'I16', 'I32', 'I64', 'U8', 'U16', 'U32', 'U64',
    'FLT', 'FLT_TYPE', 'F32', 'F64',
    'BOOL', 'BOOL_TYPE', 'TRUE', 'FALSE',
    'CHAR', 'CHAR_TYPE',
    'VOID',

    #---------------------
    # OPERATORS
    #---------------------
    'ADD', 'SUB', 'DIV', 'MUL', 'MOD',
    'LT', 'GT', 'LE', 'GE', 'NE', 'EQ',
    'AND', 'OR',
    'BIT_AND', 'BIT_OR', 'BIT_XOR', 'BIT_NOT', 'LSHFT', 'RSHFT',
    'NOT', 'UMINUS',

    #---------------------
    # KEYWORDS & OTHERS
    #---------------------
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'COLON', 'SEMICOLON', 'COMMA',
    'LET', 'CONST', 'ASSIGN', 'IDENT', 'PROCEDURE', 'WHILE', 'IF', 'ELSE', 'LAMBDA',
    'FOR', 'TERNARY', 'RETURN', 'BREAK', 'CONTINUE', 'ONSCREEN', 'SCAN',
)

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'\/'
t_MOD = r'%'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_EQ = r'\=\='
t_AND = r'\&\&'
t_OR = r'\|\|'
t_BIT_AND = r'\&'
t_BIT_OR = r'\|'
t_BIT_XOR = r'\^'
t_BIT_NOT = r'\~'
t_LSHFT = r'<<'
t_RSHFT = r'>>'
t_NOT = r"!"
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_RBRACE = r'\}'
t_LBRACE = r'\{'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_ASSIGN = r'='
t_ignore = ' \t'
t_TERNARY = r'\?'
t_ignore_COMMENT = r'//.*'

reserved_key = {
    'let' : 'LET',
    'const' : 'CONST',
    'void' : 'VOID',
    'i8' : 'I8',
    'i16' : 'I16',
    'i32' : 'I32',
    'i64' : 'I64',
    'u8' : 'U8',
    'u16' : 'U16',
    'u32' : 'U32',
    'u64' : 'U64',
    'f32' : 'F32',
    'f64' : 'F64',
    'bool' : 'BOOL_TYPE',
    'int' : 'INT_TYPE',
    'float' : 'FLT_TYPE',
    'str' : 'STR_TYPE',
    'char' : 'CHAR_TYPE',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'proc' : 'PROCEDURE',
    'procedure' : 'PROCEDURE',
    'for' : 'FOR',
    'L' : 'LAMBDA',
    'return': 'RETURN',
    'continue': 'CONTINUE',
    'break' : 'BREAK',
    'onscreen' : 'ONSCREEN',
    'scan' : 'SCAN'
}

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_key.get(t.value, "IDENT")
    return t

def t_STR(t):
    r'"([^"\\]|\\.)*"'
    t.lexer.lineno += t.value.count('\n')
    t.value = t.value[1:-1]
    return t

def t_FLT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CHAR(t):
    r"'\\?.'"
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f'Invalid Token at {t.lineno} position {t.lexpos}')
    t.lexer.skip(1)

def t_COMMENT_BLOCK(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')

lexer = lex.lex()
if __name__ == "__main__":
    data = """let x: int = 5"""
    lexer.input(data)
    while True :
        tok = lexer.token()
        if not tok:
            break
        print(tok)
