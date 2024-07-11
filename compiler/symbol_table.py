class SymbolTable:

    def __init__(self):
        self.class_scope = {'static': 0, 'field': 0}
        self.indexes = {
            'static': 0,
            'field': 0,
            'local': 0,
            'argument': 0
        }

    def start_new_subroutine(self):
        self.subroutine_scope = {'local': 0, 'argument': 0}
        self.indexes['local'] = 0
        self.indexes['argument'] = 0

    def define(self, datatype, name, kind):
        if kind in ['static', 'field']:
            self.class_scope[name] = (datatype, kind, self.indexes[kind])
        elif kind in ['local', 'argument']:
            self.subroutine_scope[name] = (datatype, kind, self.indexes[kind])
        self.indexes[kind] += 1
    
    def var_count(self, kind):
        return self.indexes[kind]
    
    def type_of(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][0]
        elif name in self.class_scope:
            return self.class_scope[name][0]
        else:
            return None

    def kind_of(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][1]
        elif name in self.class_scope:
            return self.class_scope[name][1]
        else:
            return None

    def index_of(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][2]
        elif name in self.class_scope:
            return self.class_scope[name][2]
        else:
            return None