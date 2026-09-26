from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class Symbol :
    ident : str
    type_name : str
    is_const : Optional[bool] = False
    param_type : Optional[List[str]] = None
    fields : Optional[Dict[str, str]] = None
    is_exported : bool = False



class Environment :
    def __init__(self, parent:Optional["Environment"] = None, scope:str="global"):
        self.scope =scope
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}


    def define(self, symbol):
        self.symbols[symbol.ident] = symbol


    def resolve(self, ident):
        if ident in self.symbols :
            return self.symbols[ident]
        elif self.parent is not None :
            return self.parent.resolve(ident)
        return None
