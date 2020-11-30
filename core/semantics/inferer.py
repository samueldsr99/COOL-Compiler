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
    CallNode,
    PlusNode,
    MinusNode,
    StarNode,
    DivNode,
    IsVoidNode,
    InstantiateNode,
    VariableNode,
    IntegerNode,
    StringNode,
    BooleanNode,
    LessThanNode,
    LessEqualNode,
    EqualNode,
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

    @visitor.on('node')
    def visit(self, node, type_inf=None):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        Infer all types for each class
        """
        print('ProgramNode')
        if scope is None:
            scope = Scope()

        print(f'{len(node.declarations)} declarations: {node.declarations}')
        print(f'{len(scope.children)} declarations: {scope.children}')

        for child_class in node.declarations:
            self.visit(child_class, scope.create_child())

        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        Infer all types for each attribute on the class, then for each method
        """
        print('ClassDeclarationNode')
        self.current_type = self.context.get_type(node.id)
        print(f'current_type: {self.current_type}')

        # visit attributes
        for f in node.features:
            if isinstance(f, AttrDeclarationNode):
                self.visit(f, scope)
        print('scope: ', scope.locals)
        # visit methods
        for f in node.features:
            if isinstance(f, FuncDeclarationNode):
                self.visit(f, scope.create_child())

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope=None, type_inf=None):
        """
        Infer the type of the attribute expression
        """
        print('AttrDeclarationNode')
        print(f'type for attribute: {node.type}')
        if node.expr is not None:
            expr_type = self.visit(node.expr, scope)
            print(f'expr_type: {expr_type}')

        attrib = self.current_type.get_attribute(node.id)

        if node.expr is not None and attrib.type == self.AUTO_TYPE:
            attrib.type = expr_type
            node.type = attrib.type
            print(f'Infered type {expr_type.name} for {node.id}')

        if node.type == self.AUTO_TYPE:
            self.errors.append(f'Can not infer type for {node.id}')

        print(f'defining attribute {attrib.name}, type: {attrib.type}')
        scope.define_variable(attrib.name, attrib.type, node)
        print('scope ', scope.locals)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope=None, type_inf=None):
        print('FuncDeclarationNode')
        method = self.current_type.get_method(node.id)
        self.current_method = method

        for param in node.params:
            self.visit(param, scope)

        ret_type = self.visit(node.body, scope)
        print('body type: ', type(node.body))

        print(f'method return type: {method.return_type}')
        if method.return_type == self.AUTO_TYPE:
            print('ret_type', ret_type)
            print(f'Infered type {ret_type.name} for {node.id}')
            node.return_type = ret_type.name

    @visitor.when(ConditionalNode)
    def visit(self, node, scope=None, type_inf=None):
        print('ConditionalNode')
        cond_type = self.visit(node.if_expr, scope, type_inf)
        if cond_type == self.AUTO_TYPE:
            self.errors.append(f'Can not infer type of condition')
            return self.AUTO_TYPE
        else:
            true_case = self.visit(node.then_expr, scope, type_inf)
            false_case = self.visit(node.else_expr, scope, type_inf)
            print(f'true_case: {true_case}')
            print(f'false_case: {false_case}')
            if true_case == self.AUTO_TYPE or false_case == self.AUTO_TYPE:
                return self.AUTO_TYPE
            if true_case.conforms_to(false_case):
                return false_case
            elif false_case.conforms_to(true_case):
                return true_case
            else:
                # Find LCA of two branches
                print('Finding LCA')
                a, b = true_case, false_case
                while a != b:
                    print(f'a: {a}')
                    print(f'b: {b}')
                    a = a.parent
                    b = b.parent
                print(f'type infered: {a}')
                return a

    @visitor.when(WhileNode)
    def visit(self, node, scope=None, type_inf=None):
        print('WhileNode')
        cond_type = self.visit(node.condition)
        if cond_type == self.AUTO_TYPE:
            self.errors.append(f'Cannot infer type of condition')
            return self.AUTO_TYPE
        else:
            return self.OBJECT

    @visitor.when(AssignNode)
    def visit(self, node, scope=None, type_inf=None):
        print('AssignNode')
        print(f'Finding {node.id}')
        var = scope.find_variable(node.id)
        print('scope: ', scope.locals)
        print('parent scope: ', scope.parent.locals)
        print('var: ', var)
        if var:
            expr_type = self.visit(node.expr, scope)
            print(f'expresion type: {expr_type}')
            if var.type == self.AUTO_TYPE:
                print(f'Infered type: {expr_type.name} for {node.id}')
                var.type = expr_type

                if not scope.is_local(var.name):
                    # if var is not local -> is attribute
                    print(f'updating {var.name} attribute')
                    self.current_type.update_attr_type(var.name, var.type)
                else:
                    # if var is local -> is a function param
                    print(f'updating {var.name} param')
                    self.current_type.update_function_type_param(
                        self.current_method.name,
                        var.name,
                        var.type
                    )
                # Update scope
                print(f'Updating scope')
                scope.update_var(var.name, var.type)

                return expr_type
            else:
                if not expr_type.conforms_to(var.type):
                    # Catch type error
                    self.errors.append(f'Cannot assign {expr_type} to "{var.name}" of type "{var.type}"')
                    return self.OBJECT
                else:
                    return var.type
        else:
            return self.AUTO_TYPE

    @visitor.when(BlockNode)
    def visit(self, node, scope=None, type_inf=None):
        print('BlockNode')

        ret_type = None
        for expr in node.expressions:
            ret_type = self.visit(expr, scope)

        print(f'BLOCKNODE -> Infered type: {ret_type}')
        return ret_type

    @visitor.when(VariableNode)
    def visit(self, node, scope=None, type_inf=None):
        print('VariableNode')
        if node.lex == 'self':
            node.type = self.current_type
            return node.type
        var = scope.find_variable(node.lex)

        if var:
            return var.type
        else:
            return self.AUTO_TYPE

    @visitor.when(CallNode)
    def visit(self, node, scope=None, type_inf=None):
        infered_type = None

        if node.obj is None:
            node.obj = VariableNode('self')
        obj_type = self.visit(node.obj, scope)

        if node.type is not None:
            try:
                anc_type = self.context.get_type(node.type)
            except SemanticError as e:
                anc_type = ErrorType()
            if not obj_type.conforms_to(anc_type): # Semantic error in CallNode
                infered_type = ErrorType()
        else:
            anc_type = obj_type

        try:
            method = anc_type.get_method(node.id)
        except SemanticError as e:
            method = None
            for arg in node.args:
                self.visit(arg, scope)
            infered_type = ErrorType()
        
        if method is not None:
            wrong_signature = False
            if len(node.args) != len(method.param_names):
                infered_type = ErrorType()
                wrong_signature = True
            
            for i, arg in enumerate(node.args):
                arg_type = self.visit(arg, scope)
                if not wrong_signature and not arg_type.conforms_to(method.param_types[i]):
                    infered_type = ErrorType()
        
        if method is not None:
            if method.return_type == self.AUTO_TYPE:
                if infered_type is None:
                    return self.AUTO_TYPE
                else:
                    return infered_type     # Only can be ErrorType -> SemanticError
            else:
                return method.return_type
        else:
            return infered_type

    @visitor.when(LessThanNode)
    def visit(self, node, scope=None, type_inf=None):
        print('LessThanNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(LessEqualNode)
    def visit(self, node, scope=None, type_inf=None):
        print('LessEqualNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(EqualNode)
    def visit(self, node, scope=None, type_inf=None):
        print('EqualNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(PlusNode)
    def visit(self, node, scope=None, type_inf=None):
        print('PlusNode')
        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(MinusNode)
    def visit(self, node, scope=None, type_inf=None):
        print('MinusNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(StarNode)
    def visit(self, node, scope=None, type_inf=None):
        print('StarNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(DivNode)
    def visit(self, node, scope=None, type_inf=None):
        print('DivNode')

        left = self.visit(node.left, scope, self.INTEGER)
        right = self.visit(node.right, scope, self.INTEGER)

        if left.conforms_to(self.INTEGER) and right.conforms_to(self.INTEGER):
            print(f'Infered type {self.INTEGER} for {node.operation}')
            return self.INTEGER

        print(f'Can not infer type for {node.operation}')
        return self.AUTO_TYPE

    @visitor.when(IntegerNode)
    def visit(self, node, scope=None, type_inf=None):
        print('IntegerNode')
        return self.INTEGER

    @visitor.when(StringNode)
    def visit(self, node, scope=None, type_inf=None):
        print('StringNode')
        return self.STRING

    @visitor.when(BooleanNode)
    def visit(self, node, scope=None, type_inf=None):
        print('BooleanNode')
        return self.BOOL
