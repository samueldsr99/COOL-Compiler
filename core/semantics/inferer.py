"""
AUTO_TYPE Inferer
"""
from cmp.semantic import Context, Method, Type, SemanticError, ErrorType, Scope
from cmp import visitor
import core.semantics.tools.errors as error
from core.semantics.tools.cool_ast import (
    ProgramNode,
    ClassDeclarationNode,
    AttrDeclarationNode,
    FuncDeclarationNode,
    BlockNode,
    LetNode,
    CaseNode,
    AssignNode,
    ConditionalNode,
    WhileNode,
    CallNode
)


class TypeInferer:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None

        # constants
        self.OBJECT = self.context.get_type('Object')
        self.INTEGER = self.context.get_type('Int')
        self.BOOL = self.context.get_type('Bool')
        self.STRING = self.context.get_type('String')
        self.AUTO_TYPE = self.context.get_type('AUTO_TYPE')
        self.errors = errors

    @visit.on('node')
    def visit(self, node, type_inf=None):
        pass

    @visit.when(ProgramNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        Infer all types for each class
        """
        if scope is None:
            scope = Scope()

        for child_class, child_scope in zip(node.declarations, scope.children):
            self.visit(child_class, child_scope)

        return scope

    @visit.when(ClassDeclarationNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        Infer all types for each attribute on the class, then for each method
        """
        self.current_type = self.context.get_type(node.id)

        # visit attributes
        for feature in node.features:
            if isinstance(feature, AttrDeclarationNode):
                self.visit(feature, scope)

        # visit methods
        methods = [f for f in node.features if isinstance(f, FuncDeclarationNode)]
        for method, child_scope in zip(methods, scope.children)
            self.visit(method, child_scope)

    @visit.when(AttrDeclarationNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        """
        pass
        attrib = self.current_type.get_attribute(node.id)
        scope.define_variable(attrib.name, attrib.type)
