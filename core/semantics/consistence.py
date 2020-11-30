from cmp import visitor
import core.semantics.tools.cool_ast as ast
from cmp.semantic import Context, Type, ErrorType
from core.semantics.tools import errors as error

class TypeConsistence:
    """
    Checks for cyclic inheritance.
    """
    def __init__(self, context: Context, errors: list):
        self.context: Context = context
        self.current_type: Type = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self.context.get_type(node.id)
        error_name = ErrorType().name

        ancestor = self.current_type.parent
        ancestors_visited = []
        while ancestor is not None and ancestor.name != error_name:
            if ancestor in ancestors_visited or \
            ancestor.name == self.current_type.name:
                break
            ancestors_visited.append(ancestor)
            ancestor = ancestor.parent
        if ancestor is not None and ancestor != error_name:
            self.errors.append(error.INVALID_PARENT_TYPE % (self.current_type.name, self.current_type.parent.name) + 'asdasd')
            self.current_type.parent = None
            self.current_type.set_parent(ErrorType())
