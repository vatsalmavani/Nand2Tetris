from tokenizer import Tokenizer
from symbol_table import SymbolTable

class CodeWriter:
    def __init__(self, output_file):
        self.tokenizer = Tokenizer()
        self.symbol_table = SymbolTable()
        self.file = open(output_file, 'w')
        self.compile_class()

    def compile_class(self):
        self.tokenizer.advance1('class')
        class_name = self.tokenizer.advance1('#IDENTIFIER')
        self.tokenizer.advance1('{')
        while self.tokenizer.get_token() in {'static', 'field'}:
            self.compile_class_var_dec()
        while self.tokenizer.get_token() in {'constructor', 'function', 'method'}:
            self.compile_subroutine_dec()
        self.tokenizer.advance1('}')
    
    def compile_class_var_dec(self):
        kind = self.tokenizer.advance2({'static', 'field'})
        datatype = self.tokenizer.advance1('#DATATYPE') # int, char, boolean, or className
        while True:
            var_name = self.tokenizer.advance1('#IDENTIFIER')
            self.symbol_table.define(datatype, var_name, kind)
            if self.tokenizer.get_token() == ';':
                break
            elif self.tokenizer.get_token() == ',':
                self.tokenizer.advance1(',')
        self.tokenizer.advance1(';')

    def compile_subroutine_dec(self):
        self.symbol_table.start_new_subroutine()
        subroutine_kind = self.tokenizer.advance2({'constructor', 'function', 'method'})
        return_type = self.tokenizer.advance1('#SUBROUTINE_RETURN_TYPE') # void, int, char, boolean, or className
        subroutine_name = self.tokenizer.advance1('#IDENTIFIER')
        self.tokenizer.advance1('(')
        self.compile_parameter_list()
        self.tokenizer.advance1(')')
        self.tokenizer.advance1('{')
        while self.tokenizer.get_token() == 'var':
            self.compile_var_dec()
        while self.tokenizer.get_token() in {'let', 'if', 'while', 'do', 'return'}:
            self.compile_statement()
        self.tokenizer.advance1('}')

    def compile_parameter_list(self):
        while self.tokenizer.get_token() != ')':
            datatype = self.tokenizer.advance1('#DATATYPE')
            var_name = self.tokenizer.advance1('#IDENTIFIER')
            self.symbol_table.define(datatype, var_name, 'argument')
            if self.tokenizer.get_token() == ',':
                self.tokenizer.advance1(',')

    def compile_var_dec(self):
        self.tokenizer.advance1('var')
        datatype = self.tokenizer.advance1('#DATATYPE')
        var_name = self.tokenizer.advance1('#IDENTIFIER')
        self.symbol_table.define(datatype, var_name, 'local')
        while self.tokenizer.get_token() == ',':
            self.tokenizer.advance1(',')
            var_name = self.tokenizer.advance1('#IDENTIFIER')
            self.symbol_table.define(datatype, var_name, 'local')
        self.tokenizer.advance1(';')
    
    def compile_statement(self):
        token = self.tokenizer.advance2({'let', 'if', 'while', 'do', 'return'})
        if token == 'let':
            self.compile_let()
        elif token == 'if':
            self.compile_if()
        elif token == 'while':
            self.compile_while()
        elif token == 'do':
            self.compile_do()
        else:
            self.compile_return()
    
    def compile_expression(self):
        self.compile_term()
        while self.tokenizer.get_token() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            op = self.tokenizer.advance2({'+', '-', '*', '/', '&', '|', '<', '>', '='})
            self.compile_term()
            self.write_arithmetic_op(op)
    
    def compile_term(self):
        token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type(token)
        if token_type == 'INT_CONST':
            self.file.write(f'push constant {token}')
        elif token_type == 'IDENTIFIER':
            var_kind = self.symbol_table.kind_of(token)
            var_index = self.symbol_table.index_of(token)
            self.file.write(f'push {var_kind} {var_index}')