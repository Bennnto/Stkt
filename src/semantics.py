from pathlib import Path
from parse import parser
from codegen import CodeGenerator
from lexicals import lexer
from environment import Environment, Symbol
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
    Parameter_Node,
    Procedure_Node,
    While_Node,
    Lambda_Node,
    For_Node,
    Binaryops_Node,
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
    Len_Node,
    Sync_Node,
    Export_Node
)

INTEGER_TYPES = {
    'i8', 'i16', 'i32', 'i64', 'isize',
    'u8', 'u16', 'u32', 'u64', 'usize',
}
NUMERIC_TYPES = {
    'i8', 'i16', 'i32', 'i64', 'isize',
    'u8', 'u16', 'u32', 'u64', 'usize',
    'f32', 'f64', 'int', 'float',
}


class SemanticError(Exception):
    pass


class SemanticAnalyze:
    def __init__(self):
        self.environment = Environment()
        self.current_return_type = None
        self.loop_depth = 0

    def validate_call(self, proc_symbol, node: Call_Node):
        if proc_symbol.fields is not None:
            # Struct constructor call like Point(1, 2)
            expected_count = len(proc_symbol.fields)
            actual_count = len(node.args) if node.args else 0
            if actual_count != expected_count:
                raise SemanticError(
                    f"Struct '{node.ident}' expects {expected_count} arguments, got {actual_count}"
                )
            for (f_name, f_type), arg in zip(proc_symbol.fields.items(), node.args):
                arg_type = self.infer_type(arg)
                norm_arg = "i32" if arg_type == "int" else ("f32" if arg_type == "float" else arg_type)
                if norm_arg != f_type:
                    raise SemanticError(f"Field '{f_name}' expects type '{f_type}', got '{arg_type}'")
            return

        if proc_symbol.param_type is None:
            raise SemanticError(f"'{node.ident}' is not a callable procedure")

        expected_count = len(proc_symbol.param_type)
        actual_count = len(node.args)
        if actual_count != expected_count:
            raise SemanticError(
                f"Function '{node.ident}' expects {expected_count} arguments, got {actual_count}"
            )

        for i, (expected_type, arg) in enumerate(zip(proc_symbol.param_type, node.args), start=1):
            actual_type = self.infer_type(arg)
            norm_actual = "i32" if actual_type == "int" else ("f32" if actual_type == "float" else actual_type)
            norm_expected = "i32" if expected_type == "int" else ("f32" if expected_type == "float" else expected_type)
            if norm_actual != norm_expected:
                raise SemanticError(
                    f"Function '{node.ident}' argument {i} expected '{expected_type}', got '{actual_type}'"
                )

    def analyse(self, node):
        if isinstance(node, Program_Node):
            for stmt in node.statements:
                self.analyse(stmt)

        elif isinstance(node, InterpolatedStr_Node):
            for part in node.parts:
                self.analyse(part)

        elif isinstance(node, (Int_Node, Str_Node, Float_Node, Char_Node, Bool_Node, Ident_Node)):
            self.infer_type(node)

        elif isinstance(node, Annassign_Node):
            if node.ident in self.environment.symbols:
                raise SemanticError(f"Variable '{node.ident}' is already defined in this scope")
            self.analyse(node.value)
            actual_type = self.infer_type(node.value)
            if node.type_name is not None:
                expected_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
                norm_expected = "i32" if expected_type == "int" else ("f32" if expected_type == "float" else expected_type)
                norm_actual = "i32" if actual_type == "int" else ("f32" if actual_type == "float" else actual_type)
                if norm_expected != norm_actual:
                    raise SemanticError(f"Variable '{node.ident}' declared '{expected_type}' got '{actual_type}'")
                symbol = Symbol(ident=node.ident, type_name=expected_type)
            else:
                if isinstance(node.value, Lambda_Node):
                    p_types = [p.type_name.type_name if hasattr(p.type_name, "type_name") else str(p.type_name) for p in node.value.param]
                    ret_t = node.value.return_type.type_name if hasattr(node.value.return_type, "type_name") else str(node.value.return_type)
                    symbol = Symbol(ident=node.ident, type_name=ret_t, param_type=p_types)
                else:
                    symbol = Symbol(ident=node.ident, type_name=actual_type)
            self.environment.define(symbol)

        elif isinstance(node, Assign_Node):
            var_symbol = self.environment.resolve(node.ident)
            if var_symbol is None:
                raise SemanticError(f"Variable '{node.ident}' not declared in this scope and not compatible with reassign statements")
            if var_symbol.is_const:
                raise SemanticError(f"Cannot reassign to const variable '{node.ident}'")
            self.analyse(node.value)
            new_val_type = self.infer_type(node.value)
            norm_var = "i32" if var_symbol.type_name == "int" else ("f32" if var_symbol.type_name == "float" else var_symbol.type_name)
            norm_val = "i32" if new_val_type == "int" else ("f32" if new_val_type == "float" else new_val_type)
            if norm_var != norm_val:
                raise SemanticError(f"Variable '{node.ident}' declared '{var_symbol.type_name}' cannot be assigned '{new_val_type}'")

        elif isinstance(node, Ifelse_Node):
            if_cond_type = self.infer_type(node.if_cond)
            if if_cond_type != "bool":
                raise SemanticError(f"If condition expected 'bool' type got '{if_cond_type}' type")
            if isinstance(node.if_body, list):
                for stmt in node.if_body:
                    self.analyse(stmt)
            elif node.if_body is not None:
                self.analyse(node.if_body)
            if node.else_body is not None:
                if isinstance(node.else_body, list):
                    for stmt in node.else_body:
                        self.analyse(stmt)
                else:
                    self.analyse(node.else_body)

        elif isinstance(node, Procedure_Node):
            ident = node.ident
            proc_symbol = self.environment.resolve(ident)
            if proc_symbol is not None:
                raise SemanticError(f"Procedure '{node.ident}' already defined in this scope")
            ret_type_str = node.return_type.type_name if hasattr(node.return_type, 'type_name') else str(node.return_type)
            param_types = [p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name) for p in node.param]
            proc_symbol = Symbol(ident=ident, type_name=ret_type_str, param_type=param_types, is_exported=node.is_exported)
            self.environment.define(proc_symbol)

            prev_env = self.environment
            prev_return_type = self.current_return_type
            self.environment = Environment(parent=prev_env, scope="Procedure")
            self.current_return_type = ret_type_str
            prev_loop_depth = self.loop_depth
            self.loop_depth = 0
            try:
                for p in node.param:
                    p_name = p.ident
                    p_type_name = p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name)
                    self.environment.define(Symbol(ident=p_name, type_name=p_type_name))
                if isinstance(node.body, list):
                    for stmt in node.body:
                        self.analyse(stmt)
                elif node.body is not None:
                    self.analyse(node.body)
            finally:
                self.environment = prev_env
                self.current_return_type = prev_return_type
                self.loop_depth = prev_loop_depth

        elif isinstance(node, While_Node):
            cond_type = self.infer_type(node.cond)
            if cond_type != "bool":
                raise SemanticError(f"While condition expected 'bool' type got '{cond_type}'")
            self.loop_depth += 1
            try :
                if isinstance(node.body, list):
                    for stmt in node.body:
                        self.analyse(stmt)
                elif node.body is not None:
                    self.analyse(node.body)
            finally :
                self.loop_depth -= 1

        elif isinstance(node, Lambda_Node):
            return_type = node.return_type.type_name if hasattr(node.return_type, 'type_name') else str(node.return_type)
            prev_return_type = self.current_return_type
            self.current_return_type = return_type
            prev_env = self.environment
            prev_loop_depth = self.loop_depth
            self.loop_depth = 0
            self.environment = Environment(parent=prev_env, scope="Procedure")
            try:
                for p in node.param:
                    p_name = p.ident
                    p_type = p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name)
                    param_symbol = Symbol(ident=p_name, type_name=p_type)
                    self.environment.define(param_symbol)
                if isinstance(node.body, list):
                    for stmt in node.body:
                        self.analyse(stmt)
                elif node.body is not None:
                    self.analyse(node.body)
            finally:
                self.environment = prev_env
                self.current_return_type = prev_return_type
                self.loop_depth = prev_loop_depth

        elif isinstance(node, Binaryops_Node):
            self.infer_type(node)

        elif isinstance(node, Unaryops_Node):
            self.infer_type(node)

        elif isinstance(node, For_Node):
            if node.init:
                self.analyse(node.init)
            if node.cond:
                cond_type = self.infer_type(node.cond)
                if cond_type != "bool":
                    raise SemanticError(f"For condition expected 'bool' got '{cond_type}'")
            if node.iter:
                self.analyse(node.iter)
            self.loop_depth += 1
            try:
                if isinstance(node.body, list):
                    for stmt in node.body:
                        self.analyse(stmt)
                elif node.body is not None:
                    self.analyse(node.body)
            finally :
                self.loop_depth -= 1

        elif isinstance(node, Append_Node):
            self.analyse(node.array)
            self.analyse(node.value)
            arr_t = self.infer_type(node.array)
            if not (arr_t.startswith("[") and arr_t.endswith("]")):
                raise SemanticError(f"append() first argument must be a slice, got '{arr_t}'")
            val_t = self.infer_type(node.value)
            norm_val = "i32" if val_t == "int" else ("f32" if val_t == "float" else val_t)
            elem_t = arr_t[1:-1]
            if norm_val != elem_t:
                raise SemanticError(f"cannot append '{norm_val}' to slice of type '{arr_t}'")
            return "void"

        elif isinstance(node, (Call_Node, Ternary_Node, Cast_Node)):
            self.infer_type(node)

        elif isinstance(node, Return_Node):
            if self.current_return_type is None :
                raise SemanticError("Return statement outside of a procedure or lambda")
            if node.value is not None:
                self.analyse(node.value)
                actual_type = self.infer_type(node.value)
            else:
                actual_type = "void"
            # Normalize return type int > i32 | float > f32
            norm_expected = "i32" if self.current_return_type == "int" else ("f32" if self.current_return_type == "float" else self.current_return_type)
            norm_actual = "i32" if actual_type =="int" else ("f32" if actual_type == "float" else actual_type)

            if norm_actual != norm_expected:
                raise SemanticError(
                    f"Return type mismatch: expected '{norm_expected}' got '{norm_actual}'"
                )
            return norm_actual

        elif isinstance(node, Const_Node):
            ident = node.ident
            const_symbol = self.environment.symbols.get(ident)
            if const_symbol is not None :
                raise SemanticError(f"Constant '{ident}' is already defined ")
            declared_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
            self.analyse(node.value)
            value_type = self.infer_type(node.value)
            norm_declare = "i32" if declared_type == "int" else ("f32" if declared_type == "float" else declared_type)
            norm_value = "i32" if value_type == "int" else ("f32" if value_type == "float" else value_type)
            if norm_declare != norm_value :
                raise SemanticError(f"Type mismatch: expected '{declared_type}' got '{value_type}'")
            c_symbol = Symbol(ident=ident, type_name=declared_type, is_const=True)
            self.environment.define(c_symbol)
            return norm_declare

        elif isinstance(node, Break_Node):
            if self.loop_depth <= 0:
                raise SemanticError("Break statement outside of loop")

        elif isinstance(node, Continue_Node):
            if self.loop_depth <= 0:
                raise SemanticError("Continue statement outside of loop")

        elif isinstance(node, Onscreen_Node):
            self.analyse(node.value)
            val_type = self.infer_type(node.value)
            norm_type = "i32" if val_type == "int" else ("f32" if val_type == "float" else val_type)
            if norm_type not in NUMERIC_TYPES and norm_type not in {"str", "bool", "char"}:
                raise SemanticError(f"'onscreen' does not support printing type '{val_type}'")

        elif isinstance(node, Scan_Node):
            self.infer_type(node)


        elif isinstance(node, SliceDecl_Node):
            ident = node.ident
            if ident in self.environment.symbols:
                raise SemanticError(f"Variable '{ident}' is already defined in this scope")
            elem_type = node.elem_type.type_name if hasattr(node.elem_type, "type_name") else str(node.elem_type)
            norm_elem = "i32" if elem_type == "int" else ("f32" if elem_type == "float" else elem_type)
            if node.elements:
                self.analyse(node.elements)
                elems_type = self.infer_type(node.elements)
                expected_type = f"[{norm_elem}]"
                if elems_type != expected_type:
                    raise SemanticError(f"Slice '{ident}' expected elements of type '{expected_type}', got '{elems_type}'")
            # Define as slice
            sym = Symbol(ident=ident, type_name=f"[{norm_elem}]")
            sym.is_slice = True
            self.environment.define(sym)
            return f"[{norm_elem}]"

        elif isinstance(node, Arraydecl_Node):
            ident = node.ident
            if ident in self.environment.symbols:
                raise SemanticError(f"Array '{ident}' is already defined in this scope")

            self.analyse(node.size)
            size_type = self.infer_type(node.size)
            norm_size = "i32" if size_type == "int" else size_type
            if norm_size not in INTEGER_TYPES:
                raise SemanticError(f"Array '{ident}' size must be an integer, got '{size_type}'")

            expected_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
            norm_expected = "i32" if expected_type == "int" else ("f32" if expected_type == "float" else expected_type)

            elems_list = []
            if isinstance(node.elements, Arrayliteral_Node):
                elems_list = node.elements.elements
            elif isinstance(node.elements, list):
                elems_list = node.elements

            if elems_list:
                if isinstance(node.size, Int_Node) and node.size.value != len(elems_list):
                    raise SemanticError(f"Array '{ident}' declared with size {node.size.value}, got {len(elems_list)} elements")
                for elem in elems_list:
                    self.analyse(elem)
                    elem_type = self.infer_type(elem)
                    norm_elem_type = "i32" if elem_type == "int" else ("f32" if elem_type == "float" else elem_type)
                    if norm_elem_type != norm_expected:
                        raise SemanticError(f"Element {elem} in array '{ident}' must be of type '{expected_type}', got '{elem_type}'")

            self.environment.define(Symbol(ident=ident, type_name=f"[{norm_expected}]"))
            return f"[{norm_expected}]"

        elif isinstance(node, Indexassign_Node):
            # 1. Resolve array symbol (checks current AND parent scopes)
            var_symbol = self.environment.resolve(node.ident)
            if var_symbol is None:
                raise SemanticError(f"Array '{node.ident}' not declared in this scope")

            # 2. Check constness
            if var_symbol.is_const:
                raise SemanticError(f"Cannot assign to constant array '{node.ident}'")

            # 3. Verify it is an array container: e.g. "[i32]"
            arr_type = var_symbol.type_name
            if not (arr_type.startswith("[") and arr_type.endswith("]")):
                raise SemanticError(f"Cannot index non-array variable '{node.ident}' of type '{arr_type}'")

            # 4. Extract expected element type: "[i32]" -> "i32"
            expected_elem_type = arr_type[1:-1]
            norm_expected = "i32" if expected_elem_type == "int" else ("f32" if expected_elem_type == "float" else expected_elem_type)

            # 5. Validate index expression (must be an integer)
            self.analyse(node.index)
            idx_type = self.infer_type(node.index)
            norm_idx = "i32" if idx_type == "int" else idx_type
            if norm_idx not in INTEGER_TYPES:
                raise SemanticError(f"Array index must be an integer, got '{idx_type}'")

            # 6. Validate assigned value expression type
            self.analyse(node.value)
            val_type = self.infer_type(node.value)
            norm_val_type = "i32" if val_type == "int" else ("f32" if val_type == "float" else val_type)

            if norm_val_type != norm_expected:
                raise SemanticError(
                    f"Array '{node.ident}' elements must be of type '{expected_elem_type}', got '{val_type}'"
                )

        elif isinstance(node, Match_Node):
            self.analyse(node.cond)
            cond_type = self.infer_type(node.cond)
            norm_cond = "i32" if cond_type == "int" else ("f32" if cond_type == "float" else cond_type)
            prev = self.environment
            self.environment = Environment(parent=prev, scope="Match")
            try:
                for case in node.cases :
                    if case.target is not None:
                        self.analyse(case.target)
                        target_type = self.infer_type(case.target)
                        norm_target = "i32" if target_type == "int" else ("f32" if target_type == "float" else target_type)
                        if norm_cond != norm_target:
                            raise SemanticError(f"Match pattern type mismatch expected '{norm_cond}' got '{norm_target}'")

                    if isinstance(case.body, list):
                        for stmt in case.body:
                            self.analyse(stmt)
                    elif case.body is not None :
                        self.analyse(case.body)
            finally :
                self.environment = prev
            return norm_cond

        elif isinstance(node, Loop_Node):
            self.analyse(node.time)
            time_type = self.infer_type(node.time)
            norm_time_type = "i32" if time_type == "int" else ("f32" if time_type == "float" else time_type)
            if norm_time_type not in INTEGER_TYPES:
                raise SemanticError(f"Loop time type must be an interger type got '{norm_time_type}'")
            if node.step is not None:
                self.analyse(node.step.value)
                step_type = self.infer_type(node.step.value)
                norm_step_type = "i32" if step_type == "int" else ("f32" if step_type == "float" else step_type)
                if norm_step_type not in INTEGER_TYPES:
                    raise SemanticError(f"Loop step type must be an interger type got '{norm_step_type}'")

                if isinstance(node.time, Int_Node) and isinstance(node.step.value, Int_Node):
                    if node.time.value < node.step.value.value:
                        raise SemanticError("Loop time must be greater than or equal to the step value")
            self.loop_depth += 1
            try :
                if isinstance(node.body, list):
                    for stmt in node.body:
                        self.analyse(stmt)
                elif node.body is not None :
                    self.analyse(node.body)

            finally:
                self.loop_depth -= 1
            return "void"

        elif isinstance(node, Typedecl_Node):
            if node.ident in self.environment.symbols:
                raise SemanticError(f"Type definition '{node.ident}' already declared")
            struct_fields = {}
            for field in node.field:
                if field.ident in struct_fields:
                    raise SemanticError(f"Field '{field.ident}' declared multiple times in struct '{node.ident}'")
                field_type = field.type_name.type_name if hasattr(field.type_name, 'type_name') else str(field.type_name)
                norm_field_type = "i32" if field_type == "int" else ("f32" if field_type == "float" else field_type)
                struct_fields[field.ident] = norm_field_type
            type_symbol = Symbol(
                ident = node.ident,
                type_name = node.ident,
                fields = struct_fields
            )
            self.environment.define(type_symbol)
            return "void"

        elif isinstance(node, Call_Node):
            proc_symbol = self.environment.resolve(node.ident)
            if proc_symbol is None:
                raise SemanticError(f"Procedure '{node.ident}' is not defined in this scope")

            # Allow struct instantiation like Point(1, 2)
            if proc_symbol.fields is not None:
                expected_count = len(proc_symbol.fields)
                actual_count = len(node.args) if node.args else 0
                if expected_count != actual_count:
                    raise SemanticError(
                        f"Struct '{node.ident}' expects {expected_count} arguments, got {actual_count}"
                    )
                for arg in node.args:
                    self.analyse(arg)
                return proc_symbol.type_name

            if proc_symbol.param_type is None:
                raise SemanticError(f"'{node.ident}' is not a callable procedure")

        elif isinstance(node, Export_Node):
            if self.environment.parent is not None :
                raise SemanticError("Export statements are only allowed at top level scope")
            symbol = self.environment.resolve(node.ident)
            if symbol is None :
               raise SemanticError(f"'{node.ident}' is not defined in this scope")
            symbol.is_exported = True
            return "void"

        elif isinstance(node, Sync_Node):
            if self.environment.parent is not None :
                raise SemanticError(f"Sync statements are only allowed at top level scope")
            raw_path = node.m_path.value if hasattr(node.m_path, "value") else str(node.m_path)
            module_path = Path(raw_path)

            if not module_path.exists():
                raise SemanticError(f"Module '{node.m_path} does not exist")
            with open(module_path, "r") as f:
                code = f.read()
            module_ast = parser.parse(code, lexer=lexer)
            prev_env = self.environment
            module_env = Environment(parent=prev_env, scope="Sync")
            self.environment = module_env
            try:
                self.analyse(module_ast)
            finally:
                self.environment = prev_env
                for sym in module_env.symbols.values():
                    if sym.is_exported:
                        self.environment.define(sym)
            return "void"

    def infer_type(self, node):
        if isinstance(node, Len_Node):
            arg_t = self.infer_type(node.array)
            if not (arg_t.startswith("[") and arg_t.endswith("]")) and arg_t != "str":
                raise SemanticError(f"len() requires an array, slice, or string, got '{arg_t}'")
            return "i32"

        if isinstance(node, Pop_Node):
            arg_t = self.infer_type(node.array)
            if not (arg_t.startswith("[") and arg_t.endswith("]")):
                raise SemanticError(f"pop() requires a slice or array, got '{arg_t}'")
            return arg_t[1:-1]

        if isinstance(node, Int_Node):
            return "i32"

        if isinstance(node, Float_Node):
            return "f32"

        if isinstance(node, Bool_Node):
            return "bool"

        if isinstance(node, Char_Node):
            return "char"

        if isinstance(node, (Str_Node, InterpolatedStr_Node)):
            return "str"

        if isinstance(node, Ident_Node):
            symbol = self.environment.resolve(node.ident)
            if symbol is None:
                raise NameError(f"Unknown variable '{node.ident}'")
            return symbol.type_name

        if isinstance(node, Binaryops_Node):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)

            left_type = 'i32' if left_type == 'int' else left_type
            right_type = 'i32' if right_type == 'int' else right_type
            left_type = 'f32' if left_type == 'float' else left_type
            right_type = 'f32' if right_type == 'float' else right_type

            if node.op in ("==", "!="):
                if left_type != right_type:
                    raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                return "bool"

            if node.op in ("<", ">", "<=", ">="):
                if left_type != right_type or left_type not in NUMERIC_TYPES:
                    raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                return "bool"

            if node.op in ("&&", "||"):
                if left_type != "bool" or right_type != "bool":
                    raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                return "bool"

            if node.op in ("&", "|", "^", ">>", "<<"):
                if left_type != right_type or left_type not in INTEGER_TYPES:
                    raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                return left_type

            if node.op in ("+", "-", "*", "/", "%"):
                if node.op == "+":
                    if left_type == "str" and right_type == "str":
                        return "str"
                    elif left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                        return left_type if left_type == right_type else "f32"
                    else:
                        raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                elif node.op in ("-", "*", "/", "%"):
                    if left_type != right_type or left_type not in NUMERIC_TYPES:
                        raise SemanticError(f"Operator {node.op} not compatible with '{left_type}' and '{right_type}' types")
                    return left_type

        if isinstance(node, Unaryops_Node):
            operand_type = self.infer_type(node.operand)
            norm_operand = "i32" if operand_type == "int" else ("f32" if operand_type == "float" else operand_type)
            op = getattr(node, "op", getattr(node, "ops", None))
            if op == "!":
                if norm_operand != "bool":
                    raise SemanticError(f"Operator '!' requires a 'bool' operand, got '{norm_operand}'")
                return "bool"

            op = getattr(node, "op", getattr(node, "ops", None))
            if op == "~":
                if norm_operand not in INTEGER_TYPES:
                    raise SemanticError(f"Operator '~' requrires a integer operand type got '{norm_operand}' type")
                return "int"

            op = getattr(node, "op", getattr(node, "ops", None))
            if op == "-":
                if norm_operand not in NUMERIC_TYPES:
                    raise SemanticError(f"Operator '-' requires a numeric operand type got '{norm_operand}' type")
                return "float" if norm_operand in ("f32", "f64") else "int"



        if isinstance(node, Call_Node):
            if node.ident == "len":
                if not node.args or len(node.args) != 1:
                    raise SemanticError("len() expects exactly 1 argument")
                arg_t = self.infer_type(node.args[0])
                if not (arg_t.startswith("[") and arg_t.endswith("]")) and arg_t != "str":
                    raise SemanticError(f"len() requires an array, slice, or string, got '{arg_t}'")
                return "i32"

            if node.ident == "pop":
                if not node.args or len(node.args) != 1:
                    raise SemanticError("pop() expects exactly 1 argument")
                arg_t = self.infer_type(node.args[0])
                if not (arg_t.startswith("[") and arg_t.endswith("]")):
                    raise SemanticError(f"pop() requires a slice or array, got '{arg_t}'")
                elem_t = arg_t[1:-1]
                return elem_t

            if node.ident == "append":
                if not node.args or len(node.args) != 2:
                    raise SemanticError("append() expects exactly 2 arguments (slice, value)")
                arr_t = self.infer_type(node.args[0])
                if not (arr_t.startswith("[") and arr_t.endswith("]")):
                    raise SemanticError(f"append() first argument must be a slice, got '{arr_t}'")
                val_t = self.infer_type(node.args[1])
                norm_val = "i32" if val_t == "int" else ("f32" if val_t == "float" else val_t)
                elem_t = arr_t[1:-1]
                if norm_val != elem_t:
                    raise SemanticError(f"Cannot append '{norm_val}' to slice of type '{arr_t}'")
                return "void"

            func_symbol = self.environment.resolve(node.ident)
            if func_symbol is None:
                raise SemanticError(f"Function '{node.ident}' not defined in this scope")
            self.validate_call(func_symbol, node)
            return func_symbol.type_name

        if isinstance(node, Ternary_Node):
            cond_type = self.infer_type(node.cond)
            if cond_type != "bool":
                raise SemanticError(f"Ternary condition expected 'bool' got '{cond_type}'")
            true_type = self.infer_type(node.true_block)
            false_type = self.infer_type(node.false_block)
            norm_true = "i32" if true_type == "int" else ("f32" if true_type == "float" else true_type)
            norm_false = "i32" if false_type == "int" else ("f32" if false_type == "float" else false_type)
            if norm_true != norm_false:
                raise SemanticError("Ternary branches must have the same type")
            return norm_true

        if isinstance(node, Cast_Node):
            curr_type = self.infer_type(node.value)
            target_type = node.target_type.type_name if hasattr(node.target_type, 'type_name') else str(node.target_type)
            norm_curr_type = "i32" if curr_type == "int" else ("f32" if curr_type == "float" else curr_type)
            norm_target_type = "i32" if target_type == "int" else ("f32" if target_type == "float" else target_type)

            is_numeric_cast = norm_curr_type in NUMERIC_TYPES and norm_target_type in NUMERIC_TYPES
            is_char_int_cast = (norm_curr_type == "char" and norm_target_type in INTEGER_TYPES) or (norm_curr_type in INTEGER_TYPES and norm_target_type == "char")
            is_bool_int_cast = (norm_curr_type == "bool" and norm_target_type in INTEGER_TYPES) or (norm_curr_type in INTEGER_TYPES and norm_target_type == "bool")
            if not (is_numeric_cast or is_char_int_cast or is_bool_int_cast or norm_curr_type == norm_target_type):
                raise SemanticError(f"Cannot cast type '{curr_type}' to '{target_type}'")
            return norm_target_type

        if isinstance(node, Scan_Node):
            if node.prompt is not None:
                self.analyse(node.prompt)
                prompt_type = self.infer_type(node.prompt)
                if prompt_type != "str":
                    raise SemanticError(f"'scan' prompt must be a 'str', got '{prompt_type}'")
            target_type_str = node.target_type.type_name if hasattr(node.target_type, "type_name") else str(node.target_type)
            norm_type = "i32" if target_type_str == "int" else ("f32" if target_type_str == "float" else target_type_str)
            supported = NUMERIC_TYPES | {"str", "char", "bool"}
            if norm_type not in supported:
                raise SemanticError(f"'scan' does not support type '{target_type_str}'")
            return norm_type



        if isinstance(node, Indexaccess_Node):
            arr_type = self.infer_type(node.array)
            if not (arr_type.startswith("[") and arr_type.endswith("]")):
                raise SemanticError(f"Index access must be on an array, got '{arr_type}'")

            idx_type = self.infer_type(node.index)
            norm_idx = "i32" if idx_type == "int" else idx_type
            if norm_idx not in INTEGER_TYPES:
                raise SemanticError(f"Array index must be an integer, got '{idx_type}'")

            elem_type = arr_type[1:-1]
            return elem_type


        if isinstance(node, Lambda_Node):
            ret_type = node.return_type.type_name if hasattr(node.return_type, 'type_name') else str(node.return_type)
            param_types = [p.type_name.type_name if hasattr(p.type_name, 'type_name') else str(p.type_name) for p in node.param]
            types_joined = ",".join(param_types)
            return f"fn({types_joined})->{ret_type}"

        if isinstance(node, Arrayliteral_Node):
            if not node.elements:
                return "[void]"
            first_type = self.infer_type(node.elements[0])
            norm_first = "i32" if first_type == "int" else ("f32" if first_type == "float" else first_type)
            for elem in node.elements[1:]:
                et = self.infer_type(elem)
                norm_et = "i32" if et == "int" else ("f32" if et == "float" else et)
                if norm_et != norm_first:
                    raise SemanticError(f"Array literal elements must all have the same type")
            return f"[{norm_first}]"

        if isinstance(node, Field_Node):
            self.analyse(node.ident)
            field_type = node.type_name.type_name if hasattr(node.type_name, 'type_name') else str(node.type_name)
            norm_field_type = "i32" if field_type == "int" else ("f32" if field_type == "float" else field_type)
            return norm_field_type

        if isinstance(node, Typeaccess_Node):
            # Resolve object type
            obj_name = node.ident
            obj_sym = self.environment.resolve(obj_name)
            if obj_sym is None:
                raise SemanticError(f"Variable '{obj_name}' is not defined")

            # Look up struct type
            struct_sym = self.environment.resolve(obj_sym.type_name)
            if struct_sym is None or struct_sym.fields is None:
                raise SemanticError(f"Variable '{obj_name}' of type '{obj_sym.type_name}' is not a struct")

            # Field name is node.target
            field_name = node.target.ident if hasattr(node.target, "ident") else str(node.target)
            if field_name not in struct_sym.fields:
                raise SemanticError(f"Type '{obj_sym.type_name}' has no field '{field_name}'")

            return struct_sym.fields[field_name]
