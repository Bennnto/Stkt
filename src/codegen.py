from pathlib import Path
from semantics import resolve_module_path
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
    IsOk_Node,
    SliceAccess_Node,
    Maptype_Node,
    Mapliteral_Node,
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
    Isok_Node,
    Or_Node,
    Forin_Node
)

C_TYPEMAP = {
    '[i32]': 'stkt_slice_i32',
    '[i64]': 'stkt_slice_i64',
    '[f32]': 'stkt_slice_f32',
    '[f64]': 'stkt_slice_f64',
    '[str]': 'stkt_slice_str',
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
        self.namespaces = {}
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
            "#include <ctype.h>",
            "/* Stkt Dynamic Array / Slice Runtime */",
            "#define STKT_SLICE_DEFINE(TYPE, NAME) \\",
            "typedef struct { TYPE* data; size_t len; size_t cap; } __stkt_slice_buf_##NAME; \\",
            "typedef struct { __stkt_slice_buf_##NAME* buf; } NAME;",
            "STKT_SLICE_DEFINE(int32_t, stkt_slice_i32)",
            "STKT_SLICE_DEFINE(int64_t, stkt_slice_i64)",
            "STKT_SLICE_DEFINE(float, stkt_slice_f32)",
            "STKT_SLICE_DEFINE(double, stkt_slice_f64)",
            "STKT_SLICE_DEFINE(char*, stkt_slice_str)",
            "#define STKT_SLICE_INIT(s) do { \\",
            "    (s).buf = malloc(sizeof(*((s).buf))); \\",
            "    (s).buf->data = NULL; \\",
            "    (s).buf->len = 0; \\",
            "    (s).buf->cap = 0; \\",
            "} while(0)",
            "#define STKT_SLICE_APPEND(s, val) do { \\",
            "    if ((s).buf->len >= (s).buf->cap) { \\",
            "        (s).buf->cap = ((s).buf->cap == 0) ? 4 : ((s).buf->cap * 2); \\",
            "        (s).buf->data = realloc((s).buf->data, (s).buf->cap * sizeof(*((s).buf->data))); \\",
            "    } \\",
            "    (s).buf->data[(s).buf->len++] = (val); \\",
            "} while(0)",
            "#define STKT_SLICE_POP(s) ((s).buf->data[--((s).buf->len)])",
            "#define STKT_SLICE_LEN(s) ((int32_t)((s).buf->len))",
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
            "static inline __attribute__((unused)) char* stkt_scan_str() { char* b = (char*)malloc(1024); if (!b) return \"\"; if (!fgets(b, 1024, stdin)) { b[0] = 0; return b; } size_t l = strlen(b); if (l > 0 && b[l-1] == \x27\\n\x27) b[l-1] = 0; if (l > 1 && b[l-2] == \x27\\r\x27) b[l-2] = 0; return b; }",
            "static inline __attribute__((unused)) bool stkt_scan_bool() { char b[16]; if (scanf(\"%15s\", b) != 1) return false; return (strcmp(b, \"true\") == 0 || strcmp(b, \"1\") == 0); }",
            "",
            "/* Stkt Standard File IO Runtime */",
            "static inline __attribute__((unused)) bool stkt_file_exists(const char* path) { if (!path) return false; FILE* f = fopen(path, \"r\"); if (f) { fclose(f); return true; } return false; }",
            "static inline __attribute__((unused)) bool stkt_file_write(const char* path, const char* text) { if (!path) return false; FILE* f = fopen(path, \"w\"); if (!f) return false; if (text) { fputs(text, f); } fclose(f); return true; }",
            "static inline __attribute__((unused)) char* stkt_file_read(const char* path) { if (!path) return \"\"; FILE* f = fopen(path, \"rb\"); if (!f) return \"\"; fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET); if (sz < 0) { fclose(f); return \"\"; } char* buf = (char*)malloc(sz + 1); if (!buf) { fclose(f); return \"\"; } size_t n = fread(buf, 1, sz, f); buf[n] = 0; fclose(f); return buf; }",
            "static inline __attribute__((unused)) bool stkt_file_append(const char* path, const char* text) { if (!path) return false; FILE* f = fopen(path, \"a\"); if (!f) return false; if (text) { fputs(text, f); } fclose(f); return true; }",
            "static inline __attribute__((unused)) int32_t stkt_file_size(const char* path) { if (!path) return -1; FILE* f = fopen(path, \"rb\"); if (!f) return -1; fseek(f, 0, SEEK_END); long sz = ftell(f); fclose(f); return (int32_t)sz; }",
            "",
            "/* Stkt Standard OS & Environment Runtime */",
            "static int __stkt_argc = 0;",
            "static char** __stkt_argv = NULL;",
            "static inline __attribute__((unused)) int32_t stkt_args_count() { return (int32_t)__stkt_argc; }",
            "static inline __attribute__((unused)) stkt_slice_str stkt_get_args() {",
            "    stkt_slice_str args;",
            "    STKT_SLICE_INIT(args);",
            "    for (int i = 0; i < __stkt_argc; i++) {",
            "        STKT_SLICE_APPEND(args, __stkt_argv[i]);",
            "    }",
            "    return args;",
            "}",
            "static inline __attribute__((unused)) char* stkt_get_env(const char* key) {",
            "    if (!key) return \"\";",
            "    char* v = getenv(key);\n    return v ? v : (char*)\"\";",
            "    return v ? v : \"\";",
            "}",
            "static inline __attribute__((unused)) void stkt_exit(int32_t code) { exit(code); }",
            'static inline __attribute__((unused)) char* stkt_str_concat(const char* s1, const char* s2) {\n    if (!s1) s1 = "";\n    if (!s2) s2 = "";\n    size_t len1 = strlen(s1);\n    size_t len2 = strlen(s2);\n    char* res = (char*)malloc(len1 + len2 + 1);\n    if (!res) return "";\n    memcpy(res, s1, len1);\n    memcpy(res + len1, s2, len2);\n    res[len1 + len2] = \'\\0\';\n    return res;\n}\nstatic inline __attribute__((unused)) char* stkt_str_slice(const char* s, int32_t start, int32_t end) {\n    if (!s) return "";\n    int32_t len = (int32_t)strlen(s);\n    if (start < 0) start = 0;\n    if (end > len) end = len;\n    if (start >= end) {\n        char* empty = (char*)malloc(1);\n        empty[0] = \'\\0\';\n        return empty;\n    }\n    int32_t sub_len = end - start;\n    char* res = (char*)malloc(sub_len + 1);\n    if (!res) return "";\n    memcpy(res, s + start, sub_len);\n    res[sub_len] = \'\\0\';\n    return res;\n}',
            "static inline __attribute__((unused)) stkt_slice_str stkt_str_split(const char* s, const char* sep) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!s || !sep) return res; size_t sep_len = strlen(sep); if (sep_len == 0) { STKT_SLICE_APPEND(res, strdup(s)); return res; } const char* curr = s; const char* found; while ((found = strstr(curr, sep)) != NULL) { size_t part_len = found - curr; char* part = (char*)malloc(part_len + 1); memcpy(part, curr, part_len); part[part_len] = 0; STKT_SLICE_APPEND(res, part); curr = found + sep_len; } STKT_SLICE_APPEND(res, strdup(curr)); return res; }",
            "static inline __attribute__((unused)) char* stkt_str_trim(const char* s) { if (!s) return \"\"; while (*s && isspace((unsigned char)*s)) s++; if (!*s) return strdup(\"\"); const char* end = s + strlen(s) - 1; while (end > s && isspace((unsigned char)*end)) end--; size_t len = end - s + 1; char* res = (char*)malloc(len + 1); memcpy(res, s, len); res[len] = 0; return res; }",
            "static inline __attribute__((unused)) bool stkt_str_contains(const char* s, const char* sub) { if (!s || !sub) return false; return strstr(s, sub) != NULL; }",
            "static bool __stkt_has_error = false;",
            "static inline void __stkt_set_err() { __stkt_has_error = true; }",
            "static inline void __stkt_clear_err() { __stkt_has_error = false; }",
                        "/* Stkt Hash Map Runtime */",
            "typedef struct __stkt_map_entry_str_i32 { char* key; int32_t val; struct __stkt_map_entry_str_i32* next; } __stkt_map_entry_str_i32;",
            "typedef struct { __stkt_map_entry_str_i32* buckets[64]; int32_t size; } __stkt_map_str_i32;",
            "static inline __attribute__((unused)) uint32_t __stkt_hash_str(const char* s) { uint32_t h = 2166136261u; if (!s) return 0; while (*s) { h ^= (uint8_t)*s++; h *= 16777619u; } return h; }",
            "static inline __attribute__((unused)) __stkt_map_str_i32* __stkt_map_create_str_i32() { return (__stkt_map_str_i32*)calloc(1, sizeof(__stkt_map_str_i32)); }",
            "static inline __attribute__((unused)) void __stkt_map_set_str_i32(__stkt_map_str_i32* m, const char* key, int32_t val) { if (!m || !key) return; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { curr->val = val; return; } curr = curr->next; } __stkt_map_entry_str_i32* entry = (__stkt_map_entry_str_i32*)malloc(sizeof(__stkt_map_entry_str_i32)); entry->key = strdup(key); entry->val = val; entry->next = m->buckets[idx]; m->buckets[idx] = entry; m->size++; }",
            "static inline __attribute__((unused)) int32_t __stkt_map_get_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) { __stkt_set_err(); return 0; } uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { return curr->val; } curr = curr->next; } __stkt_set_err(); return 0; }",
            "static inline __attribute__((unused)) bool __stkt_map_has_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) return false; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) return true; curr = curr->next; } return false; }",
            "static inline __attribute__((unused)) stkt_slice_str __stkt_map_keys_str_i32(__stkt_map_str_i32* m) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!m) return res; for (int i = 0; i < 64; i++) { __stkt_map_entry_str_i32* curr = m->buckets[i]; while (curr) { STKT_SLICE_APPEND(res, curr->key); curr = curr->next; } } return res; }",
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
        self.emit(f"int32_t {main_name}(int argc, char** argv) {{")
        self.indent_level += 1
        self.emit("__stkt_argc = argc;")
        self.emit("__stkt_argv = argv;")
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
        elif isinstance(node, SliceAccess_Node):
            return "str"
        elif isinstance(node, Char_Node):
            return "char"
        elif isinstance(node, Mapliteral_Node):
            return "hmap"
        elif isinstance(node, Mapliteral_Node):
            return "__stkt_map_create_str_i32()"
        elif isinstance(node, Mapliteral_Node):
            return "__stkt_map_create_str_i32()"
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
        if isinstance(node, Mapliteral_Node):
            return "__stkt_map_create_str_i32()"

        elif isinstance(node, Int_Node):
            return str(node.value)

        elif isinstance(node, Float_Node):
            return str(node.value)

        elif isinstance(node, Bool_Node):
            return "true" if node.value else "false"

        elif isinstance(node, Char_Node):
            val = str(node.value)
            if val.startswith("'") and val.endswith("'"):
                return val
            return f"'{val}'"

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
            self.emit(f"char* {buf_name} = (char*)malloc(1024);")
            self.emit(f'if ({buf_name}) snprintf({buf_name}, 1024, "{fmt_string}"{arg_str});')
            return buf_name

        elif isinstance(node, Ident_Node):
            return str(node.ident)

        elif isinstance(node, Binaryops_Node):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            lt = self.infer_expression_type(node.left)
            rt = self.infer_expression_type(node.right)
            is_lt_s = (lt == "str" or "str[" in lt)
            is_rt_s = (rt == "str" or "str[" in rt)
            if (is_lt_s or is_rt_s) and node.op in ("==", "!="):
                cmp_op = "==" if node.op == "==" else "!="
                return f"(strcmp({left}, {right}) {cmp_op} 0)"
            if is_lt_s and is_rt_s and node.op == "+":
                return f"stkt_str_concat({left}, {right})"
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
            arr_t = self.infer_expression_type(node.array)
            if arr_t == "str":
                return f"((int32_t)strlen({arr}))"
            return f"STKT_SLICE_LEN({arr})"

        elif isinstance(node, Pop_Node):
            arr = self.generate_expression(node.array)
            return f"STKT_SLICE_POP({arr})"

        elif isinstance(node, Call_Node):
            if node.ident == "len":
                arr = self.generate_expression(node.args[0])
                arr_t = self.infer_expression_type(node.args[0])
                if arr_t == "str":
                    return f"((int32_t)strlen({arr}))"
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

        elif isinstance(node, SliceAccess_Node):
            tgt = self.generate_expression(node.target)
            st = self.generate_expression(node.start)
            en = self.generate_expression(node.end)
            return f"stkt_str_slice({tgt}, {st}, {en})"

        elif isinstance(node, Indexaccess_Node):
            arr = self.generate_expression(node.array)
            idx = self.generate_expression(node.index)
            # If variable is slice, access through data pointer
            arr_var_type = self.variable.get(arr, "")
            if "stkt_slice" in arr_var_type:
                return f"{arr}.buf->data[{idx}]"
            return f"{arr}[{idx}]"

        elif isinstance(node, Typeaccess_Node):
            if isinstance(node.target, IsOk_Node):
                wrapped_call = Typeaccess_Node(ident=node.ident, target=node.target.expr)
                desugared_isok = IsOk_Node(expr=wrapped_call, msg=node.target.msg)
                return self.generate_expression(desugared_isok)
            if isinstance(node.target, Or_Node):
                wrapped_call = Typeaccess_Node(ident=node.ident, target=node.target.expr)
                desugared_or = Or_Node(expr=wrapped_call, fallback=node.target.fallback)
                return self.generate_expression(desugared_or)
            obj_t = self.variable.get(node.ident, "")
            if obj_t == "str" or obj_t.startswith("str["):
                if isinstance(node.target, Call_Node):
                    m_name = node.target.ident
                    args = [self.generate_expression(a) for a in node.target.args]
                    args_s = ", ".join(args)
                    if m_name == "split":
                        return f"stkt_str_split({node.ident}, {args_s})"
                    elif m_name == "trim":
                        return f"stkt_str_trim({node.ident})"
                    elif m_name == "contains":
                        return f"stkt_str_contains({node.ident}, {args_s})"
            if obj_t.startswith("hmap["):
                inner = obj_t[5:-1]
                parts = inner.split(":")
                k_t = parts[0].strip()
                v_t = parts[1].strip()
                if isinstance(node.target, Call_Node):
                    m_name = node.target.ident
                    args = [self.generate_expression(a) for a in node.target.args]
                    args_s = ", ".join(args)
                    if m_name == "set":
                        return f"__stkt_map_set_{k_t}_{v_t}({node.ident}, {args_s})"
                    elif m_name == "get":
                        return f"__stkt_map_get_{k_t}_{v_t}({node.ident}, {args_s})"
                    elif m_name in ("has", "has?"):
                        return f"__stkt_map_has_{k_t}_{v_t}({node.ident}, {args_s})"
                    elif m_name == "keys":
                        return f"__stkt_map_keys_{k_t}_{v_t}({node.ident})"
            if node.ident in self.namespaces:
                if isinstance(node.target, IsOk_Node):
                    wrapped_call = Typeaccess_Node(ident=node.ident, target=node.target.expr)
                    desugared_isok = IsOk_Node(expr=wrapped_call, msg=node.target.msg)
                    return self.generate_expression(desugared_isok)
                if isinstance(node.target, Or_Node):
                    wrapped_call = Typeaccess_Node(ident=node.ident, target=node.target.expr)
                    desugared_or = Or_Node(expr=wrapped_call, fallback=node.target.fallback)
                    return self.generate_expression(desugared_or)
                if isinstance(node.target, Call_Node):
                    args = [self.generate_expression(a) for a in node.target.args]
                    arg_str = ", ".join(args)
                    return f"{node.ident}_{node.target.ident}({arg_str})"
                target_str = self.generate_expression(node.target)
                return f"{node.ident}_{target_str}"
            target_str = self.generate_expression(node.target) if hasattr(node.target, "ident") else str(node.target)
            return f"{node.ident}.{target_str}"

        elif isinstance(node, IsOk_Node):
            expr_val = self.generate_expression(node.expr)
            msg_val = self.generate_expression(node.msg)
            expr_type = self.infer_expression_type(node.expr)
            c_ret_type = C_TYPEMAP.get(expr_type, "int32_t")
            temp_val = f"__val_{self.lambda_count}"
            self.lambda_count += 1
            return f"({{{c_ret_type} {temp_val} = {expr_val}; if (__stkt_has_error) {{ fprintf(stderr, \"[Error]: %s\\n\", {msg_val}); exit(1); }} {temp_val};}})"

        elif isinstance(node, Or_Node):
            expr_val = self.generate_expression(node.expr)
            fallback = self.generate_expression(node.fallback)
            expr_type = self.infer_expression_type(node.expr)
            c_type = C_TYPEMAP.get(expr_type, "int32_t")
            temp_val = f"__val_{self.lambda_count}"
            self.lambda_count += 1
            return f"({{{c_type} {temp_val} = {expr_val}; if (__stkt_has_error) {{ __stkt_clear_err();{temp_val} = {fallback}; }} {temp_val}; }})"

    def gen_Annassign_Node(self, node: Annassign_Node):
        ident = node.ident
        if node.type_name is not None:
            if isinstance(node.type_name, Maptype_Node):
                k = node.type_name.key_type.type_name if hasattr(node.type_name.key_type, "type_name") else str(node.type_name.key_type)
                v = node.type_name.val_type.type_name if hasattr(node.type_name.val_type, "type_name") else str(node.type_name.val_type)
                type_name = f"hmap[{k}:{v}]"
                c_type = f"__stkt_map_{k}_{v}*"
                self.variable[ident] = type_name
                value = self.generate_expression(node.value)
                self.emit(f"{c_type} {ident} = {value};")
                return
            type_name = node.type_name.type_name if hasattr(node.type_name, "type_name") else str(node.type_name)
            if hasattr(node.type_name, "size") and node.type_name.size is not None and node.type_name.type_name == "str":
                cap = node.type_name.size + 1
                self.variable[ident] = f"str[{node.type_name.size}]"
                value = self.generate_expression(node.value)
                self.emit(f"char {ident}[{cap}] = {value};")
                return
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
            if hasattr(p.type_name, "size") and p.type_name.size is not None and p_type == "str":
                p_c_type = "char*"
                self.variable[p_name] = f"str[{p.type_name.size}]"
            elif p_type.startswith("[") and p_type.endswith("]"):
                elem_t = p_type[1:-1]
                p_c_type = f"stkt_slice_{elem_t}"
                self.variable[p_name] = p_c_type
            else:
                p_c_type = C_TYPEMAP.get(p_type, 'int32_t')
                self.variable[p_name] = p_type
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
            self.emit(f"{node.ident}.buf->data[{idx}] = {val};")
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
        from astnodes import Arrayliteral_Node
        elem_type_str = node.elem_type.type_name if hasattr(node.elem_type, "type_name") else str(node.elem_type)
        slice_type = f"stkt_slice_{elem_type_str}"
        if slice_type not in ("stkt_slice_i32", "stkt_slice_i64", "stkt_slice_f32", "stkt_slice_f64", "stkt_slice_str"):
            slice_type = "stkt_slice_i32"
        self.variable[node.ident] = slice_type
        if node.elements is not None and not isinstance(node.elements, Arrayliteral_Node) and not isinstance(node.elements, list):
            expr_val = self.generate_expression(node.elements)
            self.emit(f"{slice_type} {node.ident} = {expr_val};")
        else:
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
        module_path = resolve_module_path(raw_path)
        with open(module_path, "r") as f:
            code = f.read()
        from parse import parser
        from lexicals import lexer
        module_ast = parser.parse(code, lexer=lexer)
        stmts = module_ast.statements if hasattr(module_ast, 'statements') else module_ast
        alias = getattr(node, "alias", None)
        if alias:
            self.namespaces[alias] = set()
        for stmt in stmts:
            if isinstance(stmt, Procedure_Node) and getattr(stmt, "is_exported", False):
                self.gen_Procedure_Node(stmt)
                self.lines.append("")
                if alias:
                    self.namespaces[alias].add(stmt.ident)
                    # Emit alias wrapper: ret_c alias_ident(params) { return ident(args); }
                    ret_type = stmt.return_type.type_name if hasattr(stmt.return_type, "type_name") else str(stmt.return_type)
                    ret_c = C_TYPEMAP.get(ret_type, "int32_t")
                    p_decls = []
                    p_args = []
                    for p in stmt.param:
                        p_t = p.type_name.type_name if hasattr(p.type_name, "type_name") else str(p.type_name)
                        p_c = f"stkt_slice_{p_t[1:-1]}" if (p_t.startswith("[") and p_t.endswith("]")) else C_TYPEMAP.get(p_t, "int32_t")
                        p_decls.append(f"{p_c} {p.ident}")
                        p_args.append(p.ident)
                    decl_str = ", ".join(p_decls) if p_decls else "void"
                    call_str = ", ".join(p_args)
                    call_stmt = f"{stmt.ident}({call_str});" if ret_c == "void" else f"return {stmt.ident}({call_str});"
                    self.emit(f"static inline {ret_c} {alias}_{stmt.ident}({decl_str}) {{ {call_stmt} }}")
                    self.lines.append("")
            elif isinstance(stmt, Typedecl_Node):
                self.gen_Typedecl_Node(stmt)
                self.lines.append("")

    def gen_Forin_Node(self, node):
        ident = node.ident
        iter_expr = self.generate_expression(node.iter)
        iter = f"__iter_1_{self.lambda_count}"
        _idx = f"__idx_{self.lambda_count}"
        self.lambda_count += 1
        self.emit(f"stkt_slice_str {iter} = {iter_expr};")
        self.emit(f"for (int32_t {_idx} = 0; {_idx} < STKT_SLICE_LEN({iter}); {_idx}++) {{")
        self.indent_level += 1
        self.variable[ident] = "str"
        self.emit(f"char* {ident} = {iter}.buf->data[{_idx}];")
        if isinstance(node.body, list):
            for stmt in node.body:
                self.generate_statement(stmt)
        elif node.body is not None:
            self.generate_statement(node.body)
        self.indent_level -= 1
        self.emit("}")
