import itertools as itt
from collections import OrderedDict


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]

class Attribute:
    def __init__(self, name, typex):
        self.name = name
        self.type = typex

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)

class Method:
    def __init__(self, name, param_names, params_types, return_type):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types

class Type:
    def __init__(self, name:str):
        self.name = name
        self.attributes = []
        self.methods = []
        self.parent = None

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name:str, from_class: str = None):
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')
            try:
                if from_class is not None and (self.parent.name == from_class or self.name == from_class):
                    raise SemanticError(f'Cyclic inheritance in class "{from_class}"')
                return self.parent.get_attribute(name, from_class)
            except SemanticError:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name:str, typex, from_class: str = None):
        try:
            self.get_attribute(name, from_class)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name:str, get_owner=False):
        try:
            meth =  next(method for method in self.methods if method.name == name)
            return meth if not get_owner else (meth, self)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name, get_owner)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name:str, param_names:list, param_types:list, return_type):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Method(name, param_names, param_types, return_type)
        self.methods.append(method)
        return method

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes:
            plain[attr.name] = (attr, self)
        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for method in self.methods:
            plain[method.name] = (method, self)
        return plain.values() if clean else plain

    def get_ancestors(self):
        if self.parent is None:
            return [self]
        else:
            return [self] + self.parent.get_ancestors()

    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def join(self, type_):
        ancestors = self.get_ancestors()
        current = type_
        while current is not None:
            if current in ancestors:
                break
            current = current.parent
        return current

    def bypass(self):
        return False

    def update_attr_type(self, name: str, new_type):
        for i, attr in enumerate(self.attributes):
            self.attributes[i].type = new_type if attr.name == name else attr.type

    def update_function_type_param(self, method: str, name: str, new_type):
        for i, method_ in enumerate(self.methods):
            if method == method_:
                m = i
                break

        for i, (param_name, param_type) in enumerate(zip(m.param_names, m.param_types)):
            if name == param_type:
                m.param_types[i] = new_type

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)

class ErrorType(Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)

class VoidType(Type):
    def __init__(self):
        Type.__init__(self, '<void>')

    def conforms_to(self, other):
        raise Exception('Invalid type: void type.')

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, VoidType)

class IntType(Type):
    def __init__(self):
        Type.__init__(self, 'int')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, IntType)

class Context:
    def __init__(self):
        self.types = {}

    def create_type(self, name:str):
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name:str):
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def __str__(self):
        return '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'

    def __repr__(self):
        return str(self)


class VariableInfo:
    def __init__(self, name, vtype, node=None):
        self.name = name
        self.type = vtype
        self.node = node
        if self.node is not None:
            self.node.type = vtype

    def __str__(self):
        return f'{self.name}: {self.type}'


class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype, node=None):
        info = VariableInfo(vname, vtype, node)
        self.locals.append(info)
        return info

    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in locals if x.name == vname)
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent is not None else None

    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.name == vname)

    def update_var(self, name: str, new_type: Type, index=None):
        if index is None:
            index = 0

        print('Updating scope: ', [local.name for local in self.locals])
        print('name ', name, 'index:', index)
        for i in range(index, len(self.locals)):
            print('current name:', self.locals[i].name)
            if self.locals[i].name == name:
                print('found', name, 'node is', self.locals[i].node)
                self.locals[i].type = new_type
                if self.locals[i].node is not None:
                    print(f'Updating type of {self.locals[i].name} from {self.locals[i].type} to {new_type}')
                    self.locals[i].node.type = new_type
                    print(f'node type: {self.locals[i].node.type}')
                return

        if self.parent:
            print('Updating parent')
            self.parent.update_var(name, new_type, self.parent.index)

    def __str__(self):
        s = 'Scope\n'
        for v in self.locals:
            s += f'{v.name}: {v.type.name}\n'
        if self.children:
            for child in self.children:
                s += str(child)
        return s
