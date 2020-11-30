from core.semantics.tools.cool_ast import ProgramNode, ClassDeclarationNode, FuncDeclarationNode, AttrDeclarationNode
from cmp.semantic import SemanticError, Context, ErrorType, Type
import core.semantics.tools.errors as error
from cmp import visitor


class TypeBuilder:
    """
    Collects attributes, methods and parent in classes.
    In case of a type error set type to ErrorType.
    """
    def __init__(self, context, errors=[]):
        self.context: Context = context
        self.current_type: Type = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        for declaration in node.declarations:
            try:
                self.visit(declaration)
            except SemanticError as e:
                self.errors.append(e.text)

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self.context.get_type(node.id)
        if node.parent is not None:
            if node.parent in ('SELF_TYPE', 'String', 'Int', 'Bool', node.id):
                self.current_type.set_parent(ErrorType())
                self.errors.append(error.INVALID_PARENT_TYPE % (node.id, node.parent))
            else:
                try:
                    parent_type = self.context.get_type(node.parent)
                except SemanticError as e:
                    parent_type = ErrorType()
                try:
                    self.current_type.set_parent(parent_type)
                except SemanticError as e:
                    self.errors.append(e.text)
        else:
            self.current_type.set_parent(self.context.get_type('Object'))

        for feature in node.features:
            self.visit(feature)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        param_names = []
        param_types = []
        for name, type_ in node.params:
            param_names.append(name)
            try:
                param_types.append(self.context.get_type(type_))
            except SemanticError as e:
                param_types.append(ErrorType())
                self.errors.append(e.text)
        try:
            ret_type = self.context.get_type(node.return_type)
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        self.current_type.define_method(node.id, param_names, param_types, ret_type)


    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            attr_type = self.context.get_type(node.type)
        except SemanticError as e:
            attr_type = ErrorType()
            self.errors.append(e.text)

        self.current_type.define_attribute(node.id, attr_type, self.current_type.name)
