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
    InterpolatedStr_Node,
    Indexaccess_Node,
    Indexassign_Node,
    Case_Node,
    Match_Node,
    Loop_Node,
    Step_Node,
    Field_Node,
    Typedecl_Node,
    Typeaccess_Node,
    SliceDecl_Node,
    Append_Node,
    Pop_Node,
    Export_Node,
    Sync_Node,
    Len_Node,
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
            "/* Stkt Dynamic Array / Slice Runtime */",
            "#define STKT_SLICE_DEFINE(TYPE, NAME) typedef struct { TYPE* data; size_t len; size_t cap; } NAME;",
            "STKT_SLICE_DEFINE(int32_t, stkt_slice_i32)",
            "STKT_SLICE_DEFINE(int64_t, stkt_slice_i64)",
            "STKT_SLICE_DEFINE(float, stkt_slice_f32)",
            "STKT_SLICE_DEFINE(double, stkt_slice_f64)",
            "STKT_SLICE_DEFINE(char*, stkt_slice_str)",
            "#define STKT_SLICE_INIT(s) do { (s).data = NULL; (s).len = 0; (s).cap = 0; } while(0)",
            "#define STKT_SLICE_APPEND(s, val) do { \\",
            "    if ((s).len >= (s).cap) { \\",
            "        (s).cap = ((s).cap == 0) ? 4 : ((s).cap * 2); \\",
            "        (s).data = realloc((s).data, (s).cap * sizeof(*(s).data)); \\",
            "    } \\",
            "    (s).data[(s).len++] = (val); \\",
            "} while(0)",
            "#define STKT_SLICE_POP(s) ((s).data[--(s).len])",
            "#define STKT_SLICE_LEN(s) ((int32_t)(s).len)",
            "",
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
            if isinstance(stmt, (Procedure_Node, Typedecl_Node)):
                self.gen_Procedure_Node(stmt)
                self.lines.append("")
            elif isinstance(stmt, Sync_Node):
                self.gen_Sync_Node(stmt)
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
        elif isinstance(node, (Str_Node, InterpolatedStr_Node)):
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

        elif isinstance(node, InterpolatedStr_Node):
            buf_name = f"__str_buf_{self.lambda_count}"
            self.lambda_count += 1
            format_specifiers = []
            c_args = []

            for part in node.parts:
                if isinstance(part, Str_Node):
                    escaped = part.value.replace("%", "%%").replace("\n", "\\n")
                    format_specifiers.append(escaped)
                else:
                    arg_type = self.infer_expression_type(part)
                    norm_type = "i32" if arg_type == "int" else ("f32" if arg_type == "float" else arg_type)
                    if norm_type in ("i32", "i16", "i8"):
                        format_specifiers.append("%d")
                    elif norm_type in ("u32", "u16", "u8"):
                        format_specifiers.append("%u")
                    elif norm_type in ("i64",):
                        format_specifiers.append("%lld")
                    elif norm_type in ("f32", "f64"):
                        format_specifiers.append("%f")
                    elif norm_type == "char":
                        format_specifiers.append("%c")
                    elif norm_type == "bool":
                        format_specifiers.append("%s")
                    else:
                        format_specifiers.append("%s")

                    expr_c = self.generate_expression(part)
                    if norm_type == "bool":
                        c_args.append(f"({expr_c} ? \"true\" : \"false\")")
                    else:
                        c_args.append(expr_c)

            fmt_string = "".join(format_specifiers)
            arg_str = ", " + ", ".join(c_args) if c_args else ""
            self.emit(f"char {buf_name}[1024];")
            self.emit(f'snprintf({buf_name}, sizeof({buf_name}), "{fmt_string}"{arg_str});')
            return buf_name

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

        elif isinstance(node, Len_Node):
            arr = self.generate_expression(node.array)
            return f"STKT_SLICE_LEN({arr})"

        elif isinstance(node, Pop_Node):
            arr = self.generate_expression(node.array)
            return f"STKT_SLICE_POP({arr})"

        elif isinstance(node, Call_Node):
            if node.ident == "len":
                arr = self.generate_expression(node.args[0])
                return f"STKT_SLICE_LEN({arr})"
            if node.ident == "pop":
                arr = self.generate_expression(node.args[0])
                return f"STKT_SLICE_POP({arr})"
            if node.ident == "append":
                arr = self.generate_expression(node.args[0])
                val = self.generate_expression(node.args[1])
                return f"STKT_SLICE_APPEND({arr}, {val})"
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
            # If variable is slice, access through data pointer
            arr_var_type = self.variable.get(arr, "")
            if "stkt_slice" in arr_var_type:
                return f"{arr}.data[{idx}]"
            return f"{arr}[{idx}]"

    def gen_Annassign_Node(self, node: Annassign_Node):
        ident = node.ident
        if node.type_name is not None:
            type_name = node.type_name.type_name if hasattr(node.type_name, "type_name") else str(node.type_name)
            c_type = C_TYPEMAP.get(type_name, "int32_t")
            self.variable[ident] = type_name
        else:
            type_name = self.infer_expression_type(node.value)
            self.variable[ident] = type_name
            if isinstance(node.value, Lambda_Node):
                # Function pointer type
                ret_t = node.value.return_type.type_name if hasattr(node.value.return_type, "type_name") else str(node.value.return_type)
                ret_c = C_TYPEMAP.get(ret_t, "int32_t")
                param_c = [C_TYPEMAP.get(p.type_name.type_name if hasattr(p.type_name, "type_name") else str(p.type_name), "int32_t") for p in node.value.param]
                param_str = ", ".join(param_c) if param_c else "void"
                value = self.generate_expression(node.value)
                self.emit(f"{ret_c} (*{ident})({param_str}) = {value};")
                return
            c_type = C_TYPEMAP.get(type_name, "int32_t")
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
        var_t = self.variable.get(node.ident, "")
        if "stkt_slice" in var_t:
            self.emit(f"{node.ident}.data[{idx}] = {val};")
        else:
            self.emit(f"{node.ident}[{idx}] = {val};")


    def gen_Match_Node(self, node:Match_Node):
        cond_type = self.infer_expression_type(node.cond)

        if cond_type in ("str", "float", "f32", "f64"):
            self.gen_match_as_if_else(node, cond_type)
        else:
            self.gen_match_as_switch(node)

    def gen_match_as_switch(self, node:Match_Node):
        cond = self.generate_expression(node.cond)
        self.emit(f"switch ({cond}) {{")
        self.indent_level += 1

        for case in node.cases :
            if case.target is not None :
                target_val = self.generate_expression(case.target)
                self.emit(f"case {target_val}: {{")
            else:
                self.emit("default: {")

            self.indent_level += 1
            if isinstance(case.body, list):
                for stmt in case.body :
                    self.generate_statement(stmt)
            elif case.body is not None :
                self.generate_statement(case.body)

            self.emit("break;")
            self.indent_level -= 1
            self.emit("}")
        self.indent_level -= 1
        self.emit("}")

    def gen_match_as_if_else(self, node: Match_Node, cond_type : str):
        cond_val = self.generate_expression(node.cond)
        temp_var = f"__match_val_{self.lambda_count}"
        self.lambda_count += 1

        c_type = "const char*" if cond_type == "str" else "float"
        self.emit(f"{c_type} {temp_var} = {cond_val};")

        first = True
        for case in node.cases :
            if case.target is not None :
                target_val = self.generate_expression(case.target)
                if cond_type == "str":
                    check = f"strcmp({temp_var}, {target_val}) == 0"
                else :
                    check = f"{temp_var} == {target_val}"
                branch = "if" if first else "else if"
                self.emit(f"{branch} ({check}) {{")
                first = False
            else :
                self.emit("else {")

            self.indent_level += 1
            if isinstance(case.body, list):
                for stmt in case.body:
                    self.generate_statement(stmt)
            elif case.body is not None :
                self.generate_statement(case.body)

            self.indent_level -= 1
            self.emit("}")

    def gen_Loop_Node(self, node: Loop_Node):
        loop_var = f"__loop_i_{self.lambda_count}"
        self.lambda_count += 1
        time = self.generate_expression(node.time)
        if node.step is not None :
            step = self.generate_expression(node.step.value)
            self.emit(f"for (int32_t {loop_var} = 0; {loop_var} < {time}; {loop_var} += {step}) {{")
        else :
            self.emit(f"for (int32_t {loop_var} = 0; {loop_var} < {time}; {loop_var}++) {{")
        self.indent_level += 1
        if isinstance(node.body, list):
            for stmt in node.body:
                self.generate_statement(stmt)
        elif node.body is not None:
            self.generate_statement(node.body)
        self.indent_level -= 1
        self.emit("}")

    def gen_Typedecl_Node(self, node: Typedecl_Node):
        old_lines = self.lines
        old_indent = self.indent_level

        # Emit at top-level functions/headers section
        self.lines = self.functions
        self.indent_level = 0

        self.emit(f"typedef struct {{")
        self.indent_level += 1
        for f in node.field:
            f_ident = f.ident
            f_type = f.type_name.type_name if hasattr(f.type_name, 'type_name') else str(f.type_name)
            f_c_type = C_TYPEMAP.get(f_type, f_type)  # Supports primitive types and nested custom types!
            self.emit(f"{f_c_type} {f_ident};")
        self.indent_level -= 1
        self.emit(f"}} {node.ident};")
        self.emit("")

        # Restore previous emission buffer and indent
        self.lines = old_lines
        self.indent_level = old_indent


    def gen_SliceDecl_Node(self, node):
        elem_type_str = node.elem_type.type_name if hasattr(node.elem_type, "type_name") else str(node.elem_type)
        slice_type = f"stkt_slice_{elem_type_str}"
        if slice_type not in ("stkt_slice_i32", "stkt_slice_i64", "stkt_slice_f32", "stkt_slice_f64", "stkt_slice_str"):
            slice_type = "stkt_slice_i32"
        self.variable[node.ident] = slice_type
        self.emit(f"{slice_type} {node.ident};")
        self.emit(f"STKT_SLICE_INIT({node.ident});")
        if node.elements:
            elems = []
            if hasattr(node.elements, "elements"):
                elems = node.elements.elements
            elif isinstance(node.elements, list):
                elems = node.elements
            for el in elems:
                v = self.generate_expression(el)
                self.emit(f"STKT_SLICE_APPEND({node.ident}, {v});")

    def gen_Append_Node(self, node):
        arr = self.generate_expression(node.array)
        val = self.generate_expression(node.value)
        self.emit(f"STKT_SLICE_APPEND({arr}, {val});")

    def gen_Sync_Node(self, node):
        raw_path = node.m_path.value if hasattr(node.m_path, "value") else str(node.m_path)
        with open(raw_path, "r") as f:
            code = f.read()
        from parse import parser
        from lexicals import lexer
        module_ast = parser.parse(code, lexer=lexer)
        stmts = module_ast.statements if hasattr(module_ast, 'statements') else module_ast
        for stmt in stmts:
            if isinstance(stmt, Procedure_Node) and getattr(stmt, "is_exported", False):
                self.gen_Procedure_Node(stmt)
                self.lines.append("")
            elif isinstance(stmt, Typedecl_Node):
                self.gen_Typedecl_Node(stmt)
                self.lines.append("")
