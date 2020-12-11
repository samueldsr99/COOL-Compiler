from cmp.semantic import Context, Method, Type, SemanticError, ErrorType, Scope
import core.semantics.tools.errors as error
from core.semantics.tools.cool_ast import *
from cmp import visitor


class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context: Context = context
        self.current_type: Type = None
        self.current_method: Method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        if scope is None:
            scope = Scope()

        # for declaration in node.declarations:
        #     self.visit(declaration, scope.create_child())

        pending = [(class_node.id, class_node) for class_node in node.declarations]
        scopes = {'IO': scope.create_child()}

        while pending:

            actual = pending.pop(0)
            type_ = self.context.get_type(actual[0])

            if type_.parent.name not in ('Object', '<error>'):
                try:
                    scopes[type_.name] = scopes[type_.parent.name].create_child()
                    self.visit(actual[1], scopes[type_.name])
                except KeyError:  # Parent not visited yet
                    pending.append(actual)
            else:
                scopes[type_.name] = scope.create_child()
                self.visit(actual[1], scopes[type_.name])

        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        self.current_type = self.context.get_type(node.id)

        for feature in node.features:
            if isinstance(feature, AttrDeclarationNode):
                self.visit(feature, scope)
            elif isinstance(feature, FuncDeclarationNode):
                self.visit(feature, scope.create_child())

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        # Check attribute override
        try:
            attr, attr_owner = self.current_type.parent.get_attribute(node.id, self.current_type.name)
            self.errors.append(error.LOCAL_ALREADY_DEFINED % (attr.name, attr_owner.name))
        except SemanticError:
            pass

        if node.id == 'self':
            self.errors.append(error.SELF_INVALID_ATTR_ID)

        try:
            attr_type = self.context.get_type(node.type) if node.type != 'SELF_TYPE' else self.current_type
        except SemanticError as e:
            attr_type = ErrorType()
            self.errors.append(e.text)

        if node.expr is not None:
            expr_type = self.visit(node.expr, scope.create_child())
            if not expr_type.conforms_to(attr_type):
                self.errors.append(error.INCOMPATIBLE_TYPES % (expr_type.name, attr_type.name))

        scope.define_variable(node.id, attr_type)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.id)
        # Check attribute override
        try:
            method, method_owner = self.current_type.parent.get_method(node.id, get_owner=True)
            if method != self.current_method:
                self.errors.append(error.WRONG_SIGNATURE % (node.id, method_owner.name))
        except SemanticError:
            pass

        scope.define_variable('self', self.current_type)

        for name, type_ in zip(self.current_method.param_names, self.current_method.param_types):
            if not scope.is_local(name):
                if type_.name == 'SELF_TYPE':
                    self.errors.append(error.INVALID_PARAM_TYPE % 'SELF_TYPE')
                    scope.define_variable(name, ErrorType())
                else:
                    scope.define_variable(name, self.context.get_type(type_.name))
            else:
                self.errors.append(error.LOCAL_ALREADY_DEFINED % (name, self.current_method.name))

        ret_type = self.context.get_type(node.return_type) if node.return_type != 'SELF_TYPE' else self.current_type

        expr_type = self.visit(node.body, scope)
        if not expr_type.conforms_to(ret_type):
            self.errors.append(error.INCOMPATIBLE_TYPES % (expr_type.name, ret_type.name))

    @visitor.when(BlockNode)
    def visit(self, node, scope):
        child_scope = scope.create_child()
        ret_type = ErrorType()
        for expr in node.expressions:
            ret_type = self.visit(expr, child_scope)
        return ret_type

    @visitor.when(LetNode)
    def visit(self, node, scope):
        for decl_node in node.declarations:
            id_ = decl_node.id
            type_ = decl_node.type
            expr = decl_node.expr
            try:
                static_type = self.context.get_type(type_) if type_ != 'SELF_TYPE' else self.current_type
            except SemanticError as e:
                static_type = ErrorType()
                self.errors.append(e.text)

            if scope.is_local(id_):
                self.errors.append(error.LOCAL_ALREADY_DEFINED % (id_, self.current_method.name))
            else:
                scope.define_variable(id_, static_type)

            expr_type = self.visit(expr, scope.create_child()) if expr is not None else None
            if expr_type is not None and not expr_type.conforms_to(static_type):
                self.errors.append(error.INCOMPATIBLE_TYPES % (expr_type.name, static_type.name))

        return self.visit(node.expr, scope.create_child())

    @visitor.when(CaseNode)
    def visit(self, node, scope):
        self.visit(node.expr, scope)
        types = []
        for id_, type_, expr in node.cases:
            new_scope = scope.create_child()
            try:
                if type_ == 'SELF_TYPE':
                    self.errors.append(error.INVALID_CASE_TYPE % type_)
            except SemanticError as e:
                new_scope.define_variable(id_, ErrorType())
                self.errors.append(e.text)
            types.append(self.visit(expr, new_scope))

        ret_type = types[0]
        for type_ in types[1:]:
            ret_type = ret_type.join(type_)
        return ret_type

    @visitor.when(AssignNode)
    def visit(self, node, scope):
        var = scope.find_variable(node.id)
        expr_type = self.visit(node.expr, scope.create_child())
        if var is None:
            self.errors.append(error.VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
        else:
            if not expr_type.conforms_to(var.type):
                self.errors.append(error.INCOMPATIBLE_TYPES % (expr_type.name, var.type.name))
        return expr_type

    @visitor.when(ConditionalNode)
    def visit(self, node, scope):
        if_type = self.visit(node.if_expr, scope)
        then_type = self.visit(node.then_expr, scope)
        esle_type = self.visit(node.else_expr, scope)

        if if_type != self.context.get_type('Bool'):
            self.errors.append(error.INCOMPATIBLE_TYPES % (if_type.name, 'Bool'))

        return then_type.join(esle_type)

    @visitor.when(WhileNode)
    def visit(self, node, scope):
        cond_type = self.visit(node.condition, scope)
        if cond_type != self.context.get_type('Bool'):
            self.errors.append(error.INCOMPATIBLE_TYPES % (cond_type.name, 'Bool'))

        self.visit(node.body, scope.create_child())

        return self.context.get_type('Object')

    @visitor.when(CallNode)
    def visit(self, node, scope):
        if node.obj is None:
            node.obj = VariableNode('self')
        obj_type = self.visit(node.obj, scope)

        if node.type is not None:
            try:
                anc_type = self.context.get_type(node.type)
            except SemanticError as e:
                anc_type = ErrorType()
                self.errors.append(e.text)
            if not obj_type.conforms_to(anc_type):
                self.errors.append(error.INVALID_ANCESTOR % (obj_type.name, anc_type.name))
        else:
            anc_type = obj_type

        try:
            method = anc_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            for arg in node.args:
                self.visit(arg, scope)
            return ErrorType()

        if len(node.args) != len(method.param_names):
            self.errors.append(error.WRONG_SIGNATURE % (method.name, obj_type.name))

        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg, scope)
            if not arg_type.conforms_to(method.param_types[i]):
                self.errors.append(error.INCOMPATIBLE_TYPES % (arg_type.name, method.param_types[i].name))

        return method.return_type if method.return_type.name != 'SELF_TYPE' else anc_type

    @visitor.when(VariableNode)
    def visit(self, node, scope):
        var = scope.find_variable(node.lex)
        if var is None:
            self.errors.append(error.VARIABLE_NOT_DEFINED % (node.lex, self.current_method.name))
            return ErrorType()
        return var.type

    @visitor.when(InstantiateNode)
    def visit(self, node, scope):
        try:
            return self.context.get_type(node.lex) if node.lex != 'SELF_TYPE' else self.current_type
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

    @visitor.when(IntegerNode)
    def visit(self, node, scope):
        return self.context.get_type('Int')

    @visitor.when(StringNode)
    def visit(self, node, scope):
        return self.context.get_type('String')

    @visitor.when(BooleanNode)
    def visit(self, node, scope):
        return self.context.get_type('Bool')

    @visitor.when(PlusNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Int')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '+', ret_type)

    @visitor.when(MinusNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Int')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '-', ret_type)

    @visitor.when(StarNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Int')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '*', ret_type)

    @visitor.when(DivNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Int')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '/', ret_type)

    @visitor.when(LessThanNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Bool')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '<', ret_type)

    @visitor.when(LessEqualNode)
    def visit(self, node, scope):
        try:
            ret_type = self.context.get_type('Bool')
        except SemanticError as e:
            ret_type = ErrorType()
            self.errors.append(e.text)

        return self._check_binary_node(node, scope, '<=', ret_type)

    @visitor.when(EqualNode)
    def visit(self, node, scope):   # TODO: fix this
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        basic_types = (self.context.get_type(type_) for type_ in ('Int', 'String', 'Bool'))

        if left_type in basic_types or right_type in basic_types:
            if left_type != right_type:
                self.errors.append(error.INCOMPATIBLE_TYPES % (left_type.name, right_type.name))

        return self.context.get_type('Bool')

    @visitor.when(IsVoidNode)
    def visit(self, node, scope):
        self.visit(node.expr, scope)
        return self.context.get_type('Bool')

    @visitor.when(NegationNode)
    def visit(self, node, scope):
        return self._check_unary_node(node, scope, 'not', self.context.get_type('Bool'))

    @visitor.when(ComplementNode)
    def visit(self, node, scope):
        return self._check_unary_node(node, scope, '~', self.context.get_type('Int'))

    def _check_binary_node(self, node, scope, oper, ret_type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if left_type == right_type == ret_type:
            return ret_type
        else:
            self.errors.append(error.INVALID_BINARY_OPER % (oper, left_type.name, right_type.name))
            return ErrorType()

    def _check_unary_node(self, node, scope, oper, expected_type):
        type_ = self.visit(node.expr, scope)
        if type_ == expected_type:
            return type_
        else:
            self.errors.append(error.INVALID_UNARY_OPER % (oper, type_))
            return ErrorType()
