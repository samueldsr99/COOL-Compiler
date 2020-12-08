
class Node:
    pass


class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations


class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
    pass


class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features


class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.return_type = return_type
        self.body = body


class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr


class ParamNode(DeclarationNode):
    def __init__(self, idx, typex):
        self.id = idx
        self.type = typex


class ParenthesisExpr(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr


class BlockNode(ExpressionNode):
    def __init__(self, expressions):
        self.expressions = expressions


class LetNode(ExpressionNode):
    def __init__(self, declarations, expr):
        self.declarations = declarations
        self.expr = expr


class CaseNode(ExpressionNode):
    def __init__(self, expr, cases):
        self.expr = expr
        self.cases = cases


class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class ConditionalNode(ExpressionNode):
    def __init__(self, ifx, then, elsex):
        self.if_expr = ifx
        self.then_expr = then
        self.else_expr = elsex


class WhileNode(ExpressionNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class CallNode(ExpressionNode):
    def __init__(self, idx, args, obj=None, typex=None):
        self.obj = obj
        self.id = idx
        self.args = args
        self.type = typex


class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex


class BinaryNode(ExpressionNode):
    def __init__(self, left, operation, right):
        self.left = left
        self.operation = operation
        self.right = right


class UnaryNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class IntegerNode(AtomicNode):
    pass


class StringNode(AtomicNode):
    pass


class BooleanNode(AtomicNode):
    pass


class PlusNode(BinaryNode):
    pass


class MinusNode(BinaryNode):
    pass


class StarNode(BinaryNode):
    pass


class DivNode(BinaryNode):
    pass


class LessThanNode(BinaryNode):
    pass


class LessEqualNode(BinaryNode):
    pass


class EqualNode(BinaryNode):
    pass


class IsVoidNode(UnaryNode):
    pass


class NegationNode(UnaryNode):
    pass


class ComplementNode(UnaryNode):
    pass
