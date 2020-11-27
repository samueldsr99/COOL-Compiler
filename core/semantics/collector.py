from cmp.semantic import Scope, Context
from tools.cool_ast import ProgramNode, ClassDeclarationNode
from cmp import visitor

class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        self.context = Context()

        # Default types definition
        self.context.create_type('AUTO_TYPE')
        self_ = self.context.create_type('SELF_TYPE')
        object_ = self.context.create_type('Object')
        io = self.context.create_type('IO')
        string = self.context.create_type('String')
        int_ = self.context.create_type('Int')
        bool_ = self.context.create_type('Bool')

        # Default types inheritance
        io.set_parent(object_)
        string.set_parent(object_)
        int_.set_parent(object_)
        bool_.set_parent(object_))

        # Default types methods
        object_.define_method('abort', [], [], object_)
        object_.define_method('type_name', [], [], string)
        object_.define_method('copy', [], [], self_)

        io.define_method('out_string', ['x'], [string], self_)
        io.define_method('out_int', ['x'], [int_], self_)
        io.define_method('in_string', [], [], string)
        io.define_method('in_int', [], [], int_)

        string.define_method('length', [], [], int_)
        string.define_method('concat', ['s'], [string], string)
        string.define_method('substr', ['i', 'l'], [int_, int_], string)

        for declaration in node.declarations:
            self.visit(declaration)       
    
    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        try:
            new_type = self.context.create_type(node.id)
        except SemanticError as e:
            self.errors.append(e.text)