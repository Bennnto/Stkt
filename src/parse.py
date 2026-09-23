import ply.yacc as yacc
from lexicals import lexer, tokens
from astnodes import (
    Program_Node,
    Int_Node,
    Str_Node,
    Float_Node,
    Bool_Node,
    Char_Node,
    Ident_Node,
    Annassign_Node,
    Type_Node,
    Assign_Node,
    Ifelse_Node,
    Parameter_Node,
    Procedure_Node,
    While_Node,
    Lambda_Node,
    Binaryops_Node,
    For_Node,
    Call_Node,
    Ternary_Node,
    Cast_Node,
    Return_Node,
    Unaryops_Node,
    Const_Node,
    Break_Node,
    Continue_Node,
    Onscreen_Node,
    Scan_Node,
    Arraydecl_Node,
    Arrayliteral_Node,
    Indexaccess_Node,
    Indexassign_Node,
)
#-----------------------------------
# PRECEDENCE
#-----------------------------------

precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "BIT_OR"),
    ("left", "BIT_XOR"),
    ("left", "BIT_AND"),
    ("left", "NE", "EQ"),
    ("left", "GT", "LT", "GE", "LE", "LSHFT", "RSHFT"),
    ("left", "ADD", "SUB"),
    ("left", "MUL", "DIV", "MOD"),
    ("right", "NOT", "BIT_NOT", "UMINUS"),
    ("left", "LBRACKET"),
)

#-----------------------------------
# PROGRAM AND STATEMENTS
#-----------------------------------

def p_program(p):
    '''program : statements'''
    p[0] = Program_Node(statements=p[1])

def p_block(p):
    '''block : LBRACE statements RBRACE'''
    p[0] = p[2]

def p_statement(p):
    '''statement : expression
                 | annassign_stmt
                 | reassign_stmt
                 | if_else_stmt
                 | procedure_stmt
                 | while_stmt
                 | for_stmt
                 | return_stmt
                 | constant_stmt
                 | break_stmt
                 | continue_stmt
                 | onscreen_stmt
                 | array_decl
                 | index_assign_stmt'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statements statement
                  | empty'''
    if len(p) == 2 :
        p[0] = []
    else :
        p[0] = p[1] + [p[2]]

#-----------------------------------
# TYPE AND LITERAL
#-----------------------------------
def p_type(p):
    '''type : I8
            | I16
            | I32
            | I64
            | U8
            | U16
            | U32
            | U64
            | F32
            | F64
            | STR_TYPE
            | INT_TYPE
            | BOOL_TYPE
            | CHAR_TYPE
            | FLT_TYPE
            | VOID'''
    p[0] = Type_Node(type_name=p[1])

def p_literals(p):
    '''expression : STR
                  | INT
                  | FLT
                  | CHAR
                  | TRUE
                  | FALSE'''
    tok_type = p.slice[1].type
    if tok_type == "INT":
        p[0] = Int_Node(value=int(p[1]))
    elif tok_type == "FLT":
        p[0] = Float_Node(value=float(p[1]))
    elif tok_type == "STR":
        p[0] = Str_Node(value=p[1])
    elif tok_type == "CHAR":
        p[0] = Char_Node(value=p[1])
    elif tok_type == "TRUE":
        p[0] = Bool_Node(value=True)
    elif tok_type == "FALSE":
        p[0] = Bool_Node(value=False)

def p_expr_ident(p):
    '''expression : IDENT'''
    p[0] = Ident_Node(ident=p[1])

def p_expr_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expr_call(p):
    '''expression : call_stmt'''
    p[0] = p[1]

def p_expr_ternary(p):
    '''expression : expression TERNARY expression COLON expression'''
    p[0] = Ternary_Node(cond=p[1], true_block=p[3], false_block=p[5])

def p_expr_cast(p):
    '''expression : LPAREN type RPAREN expression'''
    p[0] = Cast_Node(target_type=p[2], value=p[4])

#-----------------------------------
# BINARY and UNARY OPERATORS
#-----------------------------------

def p_expr_binop(p):
    '''expression : expression ADD expression
                  | expression SUB expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression
                  | expression BIT_AND expression
                  | expression BIT_OR expression
                  | expression BIT_XOR expression
                  | expression LSHFT expression
                  | expression RSHFT expression'''
    p[0] = Binaryops_Node(left=p[1], op=p[2], right=p[3])

def p_expr_unary(p):
    '''expression : SUB expression %prec UMINUS
                  | NOT expression
                  | BIT_NOT expression'''
    p[0] = Unaryops_Node(operand=p[2], op=p[1])

#-----------------------------------
# REASSIGNMENT
#-----------------------------------

def p_reassign_stmt(p):
    '''reassign_stmt : IDENT ASSIGN expression'''
    p[0] = Assign_Node(ident=p[1], value=p[3])

#-----------------------------------
# TYPE ANNOTATED ASSIGNMENT
#-----------------------------------

def p_annassign_stmt(p):
    '''annassign_stmt : LET IDENT COLON type ASSIGN expression'''
    p[0] = Annassign_Node(ident=p[2], type_name=p[4], value=p[6])

#-----------------------------------
# PROCEDURE & PARAMS
#-----------------------------------

def p_procedure_stmt(p):
    '''procedure_stmt : PROCEDURE IDENT COLON type LPAREN param_lists RPAREN block'''
    p[0] = Procedure_Node(ident=p[2], return_type=p[4], param=p[6], body=p[8])

def p_param(p):
    '''param : IDENT COLON type'''
    p[0] = Parameter_Node(ident=p[1], type_name=p[3])

def p_param_list(p):
    '''param_lists : param
                   | param_lists COMMA param
                   | empty'''
    if len(p) == 2 and p[1] != [] :
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

#-----------------------------------
# IF_ELSE
#-----------------------------------
def p_if_else_stmt(p):
    '''if_else_stmt : IF expression block ELSE block
                    | IF expression block'''
    if len(p) == 6 :
        p[0] = Ifelse_Node(if_cond=p[2], if_body=p[3], else_body=p[5])
    else:
        p[0] = Ifelse_Node(if_cond=p[2], if_body=p[3], else_body=None)

#-----------------------------------
# WHILE
#-----------------------------------
def p_while_stmt(p):
    '''while_stmt : WHILE expression block'''
    p[0] = While_Node(cond=p[2], body=p[3])

#-----------------------------------
# LAMBDA
#-----------------------------------
def p_expr_lambda(p):
    '''expression : LAMBDA COLON type LPAREN param_lists RPAREN block'''
    p[0] = Lambda_Node(param=p[5], return_type=p[3], body=p[7])

#-----------------------------------
# FOR
#-----------------------------------
def p_for_stmt(p):
    '''for_stmt : FOR expression SEMICOLON expression SEMICOLON expression block
                | FOR expression block'''
    if len(p) == 8 :
        p[0] = For_Node(init=p[2], cond=p[4], iter=p[6], body=p[7])
    elif len(p) == 4 :
        p[0] = For_Node(cond=p[2], body=p[3])

#-----------------------------------
# CALL & ARGUMENTS
#-----------------------------------
def p_call_stmt(p):
    '''call_stmt : IDENT LPAREN arg_list RPAREN'''
    p[0] = Call_Node(ident=p[1], args=p[3])

def p_argument(p):
    '''argument : expression'''
    p[0] = p[1]

def p_arg_list(p):
    '''arg_list : argument
                | arg_list COMMA argument
                | empty'''
    if len(p) == 2 and p[1] != [] :
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

#-----------------------------------
# RETURN
#-----------------------------------
def p_return_stmt(p):
    '''return_stmt : RETURN expression
                   | RETURN'''
    if len(p) == 3:
        p[0] = Return_Node(value=p[2])
    else:
        p[0] = Return_Node(value=None)

#-----------------------------------
# CONSTANT
#-----------------------------------
def p_expr_constant(p):
    '''constant_stmt : CONST type IDENT ASSIGN expression
                     | CONST IDENT COLON type ASSIGN expression'''
    if len(p) == 6:
        p[0] = Const_Node(ident=p[3], type_name=p[2], value=p[5])
    else:
        p[0] = Const_Node(ident=p[2], type_name=p[4], value=p[6])

#-----------------------------------
# BREAK AND CONTINUE
#-----------------------------------
def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = Break_Node()

def p_continue_stmt(p):
    '''continue_stmt : CONTINUE'''
    p[0] = Continue_Node()

#-----------------------------------
# ONSCREEN
#-----------------------------------
def p_onscreen_stmt(p):
    '''onscreen_stmt : ONSCREEN expression
                     | ONSCREEN LPAREN expression RPAREN'''
    p[0] = Onscreen_Node(value=p[2] if len(p) == 3 else p[3])

#-----------------------------------
# SCAN
#-----------------------------------
def p_expr_scan(p):
    '''expression : SCAN COLON type
                  | SCAN LPAREN type RPAREN
                  | SCAN LPAREN expression COMMA type RPAREN'''
    if len(p) == 4:
        # scan : type
        p[0] = Scan_Node(target_type=p[3])
    elif len(p) == 5:
        # scan(type)
        p[0] = Scan_Node(target_type=p[3])
    else:
        # scan("Enter: ", type)
        p[0] = Scan_Node(prompt=p[3], target_type=p[5])

#-----------------------------------
# ARRAY AND INDEX
#-----------------------------------
def p_element(p):
    '''element : expression'''
    p[0] = p[1]

def p_elements(p):
    '''elements : element
                | elements COMMA element
                | empty'''
    if len(p) == 2 and p[1] != []:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

def p_array_decl(p):
    '''array_decl : LET IDENT LBRACKET expression RBRACKET COLON type ASSIGN expression
                  | LET IDENT LBRACKET expression RBRACKET COLON type'''
    if len(p) == 10:
        p[0] = Arraydecl_Node(ident=p[2], size=p[4], type_name=p[7], elements=p[9])
    else:
        p[0] = Arraydecl_Node(ident=p[2], size=p[4], type_name=p[7], elements=None)

def p_expr_array_literal(p):
    '''expression : LBRACKET elements RBRACKET'''
    p[0] = Arrayliteral_Node(elements=p[2])


def p_expr_index_access(p):
    '''expression : expression LBRACKET expression RBRACKET'''
    p[0] = Indexaccess_Node(array=p[1], index=p[3])

def p_index_assign_stmt(p):
    '''index_assign_stmt : IDENT LBRACKET expression RBRACKET ASSIGN expression'''
    p[0] = Indexassign_Node(ident=p[1], index=p[3], value=p[6])


#-----------------------------------
# OTHERs
#-----------------------------------
def p_empty(p):
    '''empty : '''
    p[0] = []

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at token '{p.value}' on line {p.lineno} at position {p.lexpos}")
    else :
        raise SyntaxError("Syntax error at end of file!")

#-----------------------------------
# PARSER
#-----------------------------------
parser = yacc.yacc()
