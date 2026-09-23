from astnodes import (
    Program_Node,
    Int_Node,
    Float_Node,
    Bool_Node,
    Str_Node,
    Char_Node,
    Ident_Node,
    Annassign_Node,
    Assign_Node,
    Ifelse_Node,
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

C_TYPEMAP = {
    'i8': 'int8_t',
    'i16': 'int16_t',
    'i32': 'int32_t',
    'i64': 'int64_t',
    'u8': 'uint8_t',
    'u16': 'uint16_t',
    'u32': 'uint32_t',
    'u64': 'uint64_t',
    'int': 'int32_t',
    'f32': 'float',
    'f64': 'double',
    'float': 'float',
    'str': 'char*',
    'char': 'char',
    'bool': 'bool',
    'void': 'void',
}


class CodeGenerator:
    def __init__(self):
        self.variable = {}
        self._indent_level = 0
        self._indent_str = ""
        self.functions = []
        self.lines = []
        self.lambda_count = 0

    @property
    def indent_level(self):
        return self._indent_level

    @indent_level.setter
    def indent_level(self, value: int):
        self._indent_level = value
        self._indent_str = "    " * max(0, value)

    def indent(self):
        return self._indent_str

    def emit(self, text: str = ""):
        if text:
            self.lines.append(f"{self._indent_str}{text}")
        else:
            self.lines.append("")

    def generate(self, ast, main_name: str = "main") -> str:
        headers = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <stdint.h>",
            "#include <string.h>",
            "#include <math.h>",
            "#include <stdbool.h>",
            "#include <time.h>",
            "#include <setjmp.h>",
            "",
            "/* Stkt Standard Runtime Scanners */",
            "static inline __attribute__((unused)) int32_t stkt_scan_i32() { int32_t v = 0; if (scanf(\"%d\", &v) != 1) return 0; return v; }",
            "static inline __attribute__((unused)) uint32_t stkt_scan_u32() { uint32_t v = 0; if (scanf(\"%u\", &v) != 1) return 0; return v; }",
            "static inline __attribute__((unused)) int64_t stkt_scan_i64() { long long v = 0; if (scanf(\"%lld\", &v) != 1) return 0; return (int64_t)v; }",
            "static inline __attribute__((unused)) uint64_t stkt_scan_u64() { unsigned long long v = 0; if (scanf(\"%llu\", &v) != 1) return 0; return (uint64_t)v; }",
            "static inline __attribute__((unused)) float stkt_scan_f32() { float v = 0.0f; if (scanf(\"%f\", &v) != 1) return 0.0f; return v; }",
            "static inline __attribute__((unused)) double stkt_scan_f64() { double v = 0.0; if (scanf(\"%lf\", &v) != 1) return 0.0; return v; }",
            "static inline __attribute__((unused)) char stkt_scan_char() { char c = 0; if (scanf(\" %c\", &c) != 1) return 0; return c; }",
            "static inline __attribute__((unused)) char* stkt_scan_str() { char* b = (char*)malloc(1024); if (!b) return \"\"; if (scanf(\"%1023s\", b) != 1) b[0] = 0; return b; }",
            "static inline __attribute__((unused)) bool stkt_scan_bool() { char b[16]; if (scanf(\"%15s\", b) != 1) return false; return (strcmp(b, \"true\") == 0 || strcmp(b, \"1\") == 0); }",
        ]
        if isinstance(ast, Program_Node):
            statements = ast.statements
        elif isinstance(ast, list):
            statements = ast
        else:
            statements = [ast]

        func_lines = []
        main_lines = []

        self.functions = func_lines
        self.lines = func_lines
        self.indent_level = 0

        main_stmts = []
        for stmt in statements:
            if isinstance(stmt, Procedure_Node):
                self.gen_Procedure_Node(stmt)
                self.lines.append("")
            else:
                main_stmts.append(stmt)

        self.lines = main_lines
        self.emit(f"int32_t {main_name}() {{")
        self.indent_level += 1
        for stmt in main_stmts:
            self.generate_statement(stmt)
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")

        full_code = headers + [""] + func_lines + main_lines
        return "\n".join(full_code)

    def generate_statement(self, statement):
        method = getattr(self, f"gen_{type(statement).__name__}", None)
        if method is not None:
            method(statement)
        else:
            expr = self.generate_expression(statement)
            if expr is not None:
                self.emit(f"{expr};")
            else:
                raise TypeError(f"No code generator for {type(statement).__name__}")

    def infer_expression_type(self, node):
        if isinstance(node, Int_Node):
            return "i32"
        elif isinstance(node, Scan_Node):
            target = node.target_type.type_name if hasattr(node.target_type, "type_name") else str(node.target_type)
            return target
        elif isinstance(node, Float_Node):
            return "f32"
        elif isinstance(node, Bool_Node):
            return "bool"
        elif isinstance(node, Char_Node):
            return "char"
        elif isinstance(node, Str_Node):
            return "str"
        elif isinstance(node, Ident_Node):
            return self.variable.get(node.ident, "i32")
        elif isinstance(node, Binaryops_Node):
            lt = self.infer_expression_type(node.left)
            rt = self.infer_expression_type(node.right)
            if "f" in lt or "float" in lt or "f" in rt or "float" in rt or "double" in lt or "double" in rt:
                return "f32"
            if node.op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                return "bool"
            return lt
        return "i32"

    def generate_expression(self, node):
        if isinstance(node, Int_Node):
            return str(node.value)

        elif isinstance(node, Float_Node):
            return str(node.value)

        elif isinstance(node, Bool_Node):
            return "true" if node.value else "false"

        elif isinstance(node, Char_Node):
            return f"'{node.value}'"

        elif isinstance(node, Str_Node):
            return f'"{node.value}"'

        elif isinstance(node, Ident_Node):
            return str(node.ident)

        elif isinstance(node, Binaryops_Node):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            return f"({left} {node.op} {right})"

        elif isinstance(node, Lambda_Node):
            lambda_name = f"__lambda_{self.lambda_count}"
            self.lambda_count += 1

            # Build Param list
            params = []
            for p in node.param:
                p_type = p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name)
                c_t = C_TYPEMAP.get(p_type, 'int32_t')
                params.append(f"{c_t} {p.ident}")
            param_str = ", ".join(params) if params else "void"
            ret_type_str = node.return_type.type_name if hasattr(node.return_type, 'type_name') else str(node.return_type)
            ret_type = C_TYPEMAP.get(ret_type_str, 'int32_t')

            old_lines = self.lines
            self.lines = self.functions
            self.emit(f"static {ret_type} {lambda_name}({param_str}) {{")
            self.indent_level += 1

            if isinstance(node.body, list):
                for stmt in node.body:
                    self.generate_statement(stmt)
            else:
                expr_val = self.generate_expression(node.body)
                self.emit(f"return {expr_val};")

            self.indent_level -= 1
            self.emit("}")
            self.emit("")

            self.lines = old_lines
            return lambda_name

        elif isinstance(node, Call_Node):
            args = [self.generate_expression(arg) for arg in node.args]
            arg_str = ", ".join(args)
            return f"{node.ident}({arg_str})"

        elif isinstance(node, Ternary_Node):
            cond = self.generate_expression(node.cond)
            true_block = self.generate_expression(node.true_block)
            false_block = self.generate_expression(node.false_block)
            return f"({cond} ? {true_block} : {false_block})"

        elif isinstance(node, Cast_Node):
            value = self.generate_expression(node.value)
            target_type = node.target_type.type_name if hasattr(node.target_type, 'type_name') else str(node.target_type)
            target_c_type = C_TYPEMAP.get(target_type, "int32_t")
            return f"(({target_c_type})({value}))"

        elif isinstance(node, Unaryops_Node):
            operand = self.generate_expression(node.operand)
            ops = node.op
            return f"({ops}{operand})"

        elif isinstance(node, Scan_Node):
            target = node.target_type.type_name if hasattr(node.target_type, "type_name") else str(node.target_type)
            norm = "i32" if target == "int" else ("f32" if target == "float" else target)
            if norm in {"i8", "i16", "i32"}:
                fn = "stkt_scan_i32()"
            elif norm in {"u8", "u16", "u32"}:
                fn = "stkt_scan_u32()"
            elif norm == "i64":
                fn = "stkt_scan_i64()"
            elif norm == "u64":
                fn = "stkt_scan_u64()"
            elif norm == "f32":
                fn = "stkt_scan_f32()"
            elif norm == "f64":
                fn = "stkt_scan_f64()"
            elif norm == "str":
                fn = "stkt_scan_str()"
            elif norm == "char":
                fn = "stkt_scan_char()"
            elif norm == "bool":
                fn = "stkt_scan_bool()"
            else:
                fn = "stkt_scan_i32()"

            if node.prompt is not None:
                prompt_val = self.generate_expression(node.prompt)
                return f"(printf(\"%s\", {prompt_val}), fflush(stdout), {fn})"
            return fn

        elif isinstance(node, Arrayliteral_Node):
            elems = [self.generate_expression(e) for e in node.elements]
            return "{" + ", ".join(elems) + "}"

        elif isinstance(node, Indexaccess_Node):
            arr = self.generate_expression(node.array)
            idx = self.generate_expression(node.index)
            return f"{arr}[{idx}]"

    def gen_Annassign_Node(self, node: Annassign_Node):
        ident = node.ident
        type_name = node.type_name.type_name if hasattr(node.type_name, "type_name") else str(node.type_name)
        c_type = C_TYPEMAP.get(type_name, "int32_t")
        self.variable[ident] = type_name
        value = self.generate_expression(node.value)
        self.emit(f"{c_type} {ident} = {value};")

    def gen_Assign_Node(self, node: Assign_Node):
        ident = node.ident
        if ident not in self.variable:
            self.variable[ident] = self.infer_expression_type(node.value)
        value = self.generate_expression(node.value)
        self.emit(f"{ident} = {value};")

    def gen_Ifelse_Node(self, node: Ifelse_Node):
        if_cond = self.generate_expression(node.if_cond)
        self.emit(f"if ({if_cond}) {{")
        self.indent_level += 1
        if isinstance(node.if_body, list):
            for stmt in node.if_body:
                self.generate_statement(stmt)
        elif node.if_body is not None:
            self.generate_statement(node.if_body)
        self.indent_level -= 1
        self.emit("}")

        if node.else_body is not None:
            self.emit("else {")
            self.indent_level += 1
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self.generate_statement(stmt)
            else:
                self.generate_statement(node.else_body)
            self.indent_level -= 1
            self.emit("}")

    def gen_Procedure_Node(self, node: Procedure_Node):
        ident = node.ident
        return_type = node.return_type.type_name if hasattr(node.return_type, 'type_name') else str(node.return_type)
        return_c_type = C_TYPEMAP.get(return_type, "int32_t")
        param_list = []
        for p in node.param:
            p_name = p.ident
            p_type = p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name)
            p_c_type = C_TYPEMAP.get(p_type, 'int32_t')
            param_list.append(f"{p_c_type} {p_name}")
        param_str = ", ".join(param_list) if param_list else "void"

        self.emit(f"{return_c_type} {ident} ({param_str}) {{")
        self.indent_level += 1
        if isinstance(node.body, list):
            for stmt in node.body:
                self.generate_statement(stmt)
        elif node.body is not None:
            self.generate_statement(node.body)

        self.indent_level -= 1
        self.emit("}")

    def gen_While_Node(self, node: While_Node):
        cond = self.generate_expression(node.cond)
        self.emit(f"while ({cond}) {{")
        self.indent_level += 1
        if isinstance(node.body, list):
            for stmt in node.body:
                self.generate_statement(stmt)
        elif node.body is not None:
            self.generate_statement(node.body)
        self.indent_level -= 1
        self.emit("}")

    def gen_For_Node(self, node: For_Node):
        cond = self.generate_expression(node.cond)
        if node.init is not None:
            init = self.generate_expression(node.init)
            iter_expr = self.generate_expression(node.iter)
            self.emit(f"for({init};{cond};{iter_expr}) {{")
            self.indent_level += 1
            if isinstance(node.body, list):
                for stmt in node.body:
                    self.generate_statement(stmt)
            elif node.body is not None:
                self.generate_statement(node.body)
            self.indent_level -= 1
            self.emit("}")
        else:
            self.emit(f"while({cond}){{")
            self.indent_level += 1
            if isinstance(node.body, list):
                for stmt in node.body:
                    self.generate_statement(stmt)
            elif node.body is not None:
                self.generate_statement(node.body)
            self.indent_level -= 1
            self.emit("}")

    def gen_Call_Node(self, node: Call_Node):
        call_expr = self.generate_expression(node)
        self.emit(f"{call_expr};")

    def gen_Ternary_Node(self, node: Ternary_Node):
        expr = self.generate_expression(node)
        self.emit(f"{expr};")

    def gen_Return_Node(self, node: Return_Node):
        if node.value is not None:
            value = self.generate_expression(node.value)
            self.emit(f"return {value};")
        else:
            self.emit(f"return;")

    def gen_Const_Node(self, node: Const_Node):
        ident = node.ident
        value = self.generate_expression(node.value)
        con_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
        con_c_type = C_TYPEMAP.get(con_type, "int32_t")
        self.variable[ident] = con_c_type
        self.emit(f"const {con_c_type} {ident} = {value};")

    def gen_Break_Node(self, node: Break_Node):
        self.emit('break;')

    def gen_Continue_Node(self, node: Continue_Node):
        self.emit('continue;')

    def gen_Onscreen_Node(self, node:Onscreen_Node):
        val = self.generate_expression(node.value)
        val_type = self.infer_expression_type(node.value)

        if val_type in {"i8", "i16", "i32", "int"}:
            self.emit(f'printf("%d\\n", (int32_t)({val}));')
        elif val_type in {"u8", "u16", "u32"}:
            self.emit(f'printf("%u\\n", (uint32_t)({val}));')
        elif val_type in {"i64"}:
            self.emit(f'printf("%lld\\n", (long long)({val}));')
        elif val_type in {"u64"}:
            self.emit(f'printf("%llu\\n", (unsigned long long)({val}));')
        elif val_type in {"f32", "float"}:
            self.emit(f'printf("%f\\n", (float)({val}));')
        elif val_type in {"f64"}:
            self.emit(f'printf("%lf\\n", (double)({val}));')
        elif val_type == "str":
            self.emit(f'printf("%s\\n", {val});')
        elif val_type == "char":
            self.emit(f'printf("%c\\n", {val});')
        elif val_type == "bool":
            self.emit(f'printf("%s\\n", ({val}) ? "true" : "false");')
        else:
            self.emit(f'printf("%d\\n", {val});')

    def gen_Arraydecl_Node(self, node:Arraydecl_Node):
        ident = node.ident
        size = self.generate_expression(node.size)
        arr_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
        arr_c_type = C_TYPEMAP.get(arr_type, "int32_t")
        self.variable[node.ident] = f"[{arr_type}]"
        if node.elements is not None :
            element_str = self.generate_expression(node.elements)
            self.emit(f"{arr_c_type} {ident}[{size}] = {element_str};")
        else:
            self.emit(f"{arr_c_type} {ident}[{size}] = {{0}};")


    def gen_Indexassign_Node(self, node: Indexassign_Node):
        idx = self.generate_expression(node.index)
        val = self.generate_expression(node.value)
        self.emit(f"{node.ident}[{idx}] = {val};")
