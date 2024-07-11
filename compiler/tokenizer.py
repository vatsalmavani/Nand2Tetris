import re


class Tokenizer:

    KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var",
                    "int", "char", "boolean", "void", "true", "false", "null", "this", "let",
                    "do", "if", "else", "while", "return"}
    SYMBOLS = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"}

    def __init__(self, string):
        self.current_token_index = -1
        self.tokens = self.tokenize(string)

    def tokenize(self, string):
        string = re.sub(r'//.*\n', '', string) # remove inline comments
        string = re.sub(r'/\*.*?\*/', '', string, flags=re.DOTALL) # remove multiline comments
        pattern = r'(".*?"|\b\w+\b|[{}()\[\].,;+\-*/&|<>=~])' # match with either a string constant, a word or a punctuation/operator
        tokens = re.findall(pattern, string)
        return tokens
        
    def _has_more_tokens(self):
        return self.current_token_index < len(self.tokens)
    
    def get_token(self):
        if self._has_more_tokens():
            return self.tokens[self.current_token_index]
        raise IndexError("No more tokens available")
    
    def _is_valid_var_name(self, variable):
        if variable in Tokenizer.KEYWORDS:
            return False
        if not (variable[0].isalpha() or variable[0] == '_'):
            return False
        if not all(c.isalnum() or c == '_' for c in variable):
            return False
        return True

    def _is_valid_datatype(self, datatype):
        if datatype in ['int', 'char', 'boolean']:
            return True
        if self._is_valid_var_name(datatype):
            return True
        return False
    
    def _is_valid_return_type(self, return_type):
        if return_type == 'void':
            return True
        if self._is_valid_datatype(return_type):
            return True
        return False

    def advance1(self, expected_token):
        self.current_token_index += 1
        token = self.get_token()
        if expected_token == "#IDENTIFIER":
            if self._is_valid_var_name(token):
                return token
            raise SyntaxError(f"Invalid variable name: '{token}'")
        if expected_token == "#DATATYPE":
            # TODO: make sure that datatype is from set of classnames
            if self._is_valid_datatype(token):
                return token
            raise SyntaxError(f"Invalid data type: '{token}'")
        if expected_token == '#SUBROUTINE_RETURN_TYPE':
            if self._is_valid_return_type(token):
                return token
            raise SyntaxError(f"Invalid return type: '{token}")
        if token != expected_token:
            raise SyntaxError(f"Unexpected token: '{token}'")
        return token
    
    def advance2(self, expected_tokens_list):
        self.current_token_index += 1
        token = self.get_token()
        for expected_token in expected_tokens_list:
            if token == expected_token:
                return token
        raise SyntaxError(f"Unexpected token: '{token}'")

    def token_type(self, token):
        if token in self.KEYWORDS:
            return 'KEYWORD'
        elif token in self.SYMBOLS:
            return 'SYMBOL'
        elif token.isdigit():
            return 'INT_CONST'
        elif token.startswith('"'):
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'