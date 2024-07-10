from tokenizer import Tokenizer
from symbol_table import SymbolTable

class CodeWriter:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.symbol_table = SymbolTable()

    def compile_class(self):
        self.tokenizer.advance1('class')
        class_name = self.tokenizer.advance1('IDENTIFIER')
        self.tokenizer.advance1('{')
        while self.tokenizer.get_token() in ['static', 'field']:
            self.compile_class_var_dec()
        while self.tokenizer.get_token() in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()
        self.tokenizer.advance1('}')
    
    def compile_class_var_dec(self):
        kind = self.tokenizer.advance2(['static', 'field'])
        datatype = self.tokenizer.advance1('DATATYPE') # int, char, boolean, or className
        while True:
            var_name = self.tokenizer.advance1('IDENTIFIER')
            self.symbol_table.define(datatype, var_name, kind)
            if self.tokenizer.get_token() == ';':
                break
            elif self.tokenizer.get_token() == ',':
                self.tokenizer.advance1(',')
        self.tokenizer.advance1(';')

    def compile_subroutine_dec(self):
        self.symbol_table.start_new_subroutine()
        subroutine_kind = self.tokenizer.advance2(['constructor', 'function', 'method'])
        return_type = self.tokenizer.advance1('SUBROUTINE_RETURN_TYPE') # void, int, char, boolean, or className
        self.tokenizer.advance1('IDENTIFIER')
        self.tokenizer.advance1('(')
        self.compile_parameter_list()
        self.tokenizer.advance1(')')
        
