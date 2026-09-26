from dataclasses import dataclass, field
from typing import Optional, List

class Node:
    pass

@dataclass
class Program_Node(Node):
    statements : List[Node]

@dataclass
class Int_Node(Node):
    value : int

@dataclass
class Str_Node(Node):
    value : str

@dataclass
class Char_Node(Node):
    value : str

@dataclass
class Float_Node(Node):
    value : float

@dataclass
class Bool_Node(Node):
    value : bool

@dataclass
class Ident_Node(Node):
    ident : str

@dataclass
class Type_Node(Node):
    type_name : str

@dataclass
class Annassign_Node(Node):
    ident : str
    type_name : Type_Node
    value : Node

@dataclass
class Assign_Node(Node):
    ident : str
    value : Node

@dataclass
class Ifelse_Node(Node):
    if_cond : Node
    if_body : List[Node]
    else_body : Optional[List[Node]]

@dataclass
class Parameter_Node(Node):
    ident : str
    type_name : Type_Node

@dataclass
class Procedure_Node(Node):
    ident : str
    return_type : Type_Node
    param : List[Parameter_Node]
    body : List[Node]
    is_exported : bool = False

@dataclass
class While_Node(Node):
    cond : Node
    body : List[Node]

@dataclass
class Lambda_Node(Node):
    param : List[Parameter_Node]
    return_type : Type_Node
    body : List[Node]

@dataclass
class Binaryops_Node(Node):
    left : Node
    op : str
    right : Node

@dataclass
class Call_Node(Node):
    ident : str
    args : List[Node]

@dataclass
class For_Node(Node):
    cond : Node
    init : Optional[Node] = None
    iter : Optional[Node] = None
    body : List[Node] = field(default_factory=list)

@dataclass
class Ternary_Node(Node):
    cond : Node
    true_block : Node
    false_block : Node

@dataclass
class Cast_Node(Node):
    target_type : Type_Node
    value : Node

@dataclass
class Return_Node(Node):
    value : Optional[Node] = None

@dataclass
class Unaryops_Node(Node):
    operand : Node
    op : str

@dataclass
class Const_Node(Node):
    ident : str
    type_name : Type_Node
    value : Node

@dataclass
class Break_Node(Node):
    pass

@dataclass
class Continue_Node(Node):
    pass

@dataclass
class Onscreen_Node(Node):
    value : Node

@dataclass
class Scan_Node(Node):
    target_type : Type_Node
    prompt : Optional[Node] = None

@dataclass
class Arraydecl_Node(Node):
    ident : str
    size : int
    type_name : Type_Node
    elements : Optional[Node] = None

@dataclass
class Arrayliteral_Node(Node):
    elements : List[Node]


@dataclass
class Indexaccess_Node(Node):
    array : Node
    index : Node


@dataclass
class Indexassign_Node(Node):
    ident : str
    index : Node
    value : Node


@dataclass
class Case_Node(Node):
    body : List[Node]
    target : Optional[Node] = None


@dataclass
class Match_Node(Node):
    cond : Node
    cases : List[Case_Node]


@dataclass
class InterpolatedStr_Node(Node):
    parts : List[Node]


@dataclass
class Step_Node(Node):
    value : Node


@dataclass
class Loop_Node(Node):
    time : Node
    body : List[Node]
    step : Optional[Step_Node] = None


@dataclass
class Field_Node(Node):
    ident : str
    type_name : Type_Node

@dataclass
class Typedecl_Node(Node):
    ident : str
    field : List[Field_Node]

@dataclass
class Typeaccess_Node(Node):
    ident : str
    target : Node

@dataclass
class Append_Node(Node):
    array : Node
    value : Node

@dataclass
class Pop_Node(Node):
    array : Node

@dataclass
class Len_Node(Node):
    array : Node

@dataclass
class SliceDecl_Node(Node):
    ident : str
    elem_type : Type_Node
    elements : Optional[Node] = None

@dataclass
class Export_Node(Node):
    decl : Node

@dataclass
class Sync_Node(Node):
    m_path : str
    alias : Optional[str] = None
