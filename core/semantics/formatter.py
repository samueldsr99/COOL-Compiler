import cmp.visitor as visitor
from core.semantics.tools.cool_ast import *


class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<class> ... <class>]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, tabs=0):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '\t' * tabs + f'\\__ClassDeclarationNode: class {node.id} {parent} {{ <feature> ... <feature> }}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.type}'
        return f'{ans}'

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        params = ', '.join(':'.join(param) for param in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: {node.id}({params}) : {node.return_type} -> <body>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(LetNode)
    def visit(self, node, tabs=0):
        declarations = []
        for _id, _type, _expr in node.declarations:
            if _expr is not None:
                declarations.append(
                    '\t' * tabs +
                    f'\\__VarDeclarationNode: {_id}: {_type} <-\n{self.visit(_expr, tabs + 1)}'
                )
            else:
                declarations.append('\t' * tabs +
                                    f'\\__VarDeclarationNode: {_id} : {_type}')
        declarations = '\n'.join(declarations)
        ans = '\t' * tabs + f'\\__LetNode:  let'
        expr = self.visit(node.expr, tabs + 2)
        return f'{ans}\n {declarations}\n' + '\t' * (tabs +
                                                       1) + 'in\n' + f'{expr}'

    @visitor.when(AssignNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AssignNode: {node.id} <- <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(BlockNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__BlockNode:'
        body = '\n'.join(
            self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}\n{body}'

    @visitor.when(ConditionalNode)
    def visit(self, node, tabs=0):
        ifx = self.visit(node.if_expr, tabs + 2)
        then = self.visit(node.then_expr, tabs + 2)
        elsex = self.visit(node.else_expr, tabs + 2)

        return '\n'.join([
            '\t' * tabs +
            f'\\__ConditionalNode: if <expr> then <expr> else <expr> fi',
            '\t' * (tabs + 1) + f'\\__if \n{ifx}',
            '\t' * (tabs + 1) + f'\\__then \n{then}',
            '\t' * (tabs + 1) + f'\\__else \n{elsex}',
        ])

    @visitor.when(WhileNode)
    def visit(self, node, tabs=0):
        condition = self.visit(node.condition, tabs + 2)
        body = self.visit(node.body, tabs + 2)

        return '\n'.join([
            '\t' * tabs + f'\\__WhileNode: while <expr> loop <expr> pool',
            '\t' * (tabs + 1) + f'\\__while \n{condition}',
            '\t' * (tabs + 1) + f'\\__loop \n{body}',
        ])

    @visitor.when(CaseNode)
    def visit(self, node, tabs=0):
        cases = []
        for _id, _type, _expr in node.cases:
            expr = self.visit(_expr, tabs + 3)
            cases.append('\t' * tabs +
                         f'\\__CaseNode: {_id} : {_type} =>\n{expr}')
        expr = self.visit(node.expr, tabs + 2)
        cases = '\n'.join(cases)

        return '\n'.join([
            '\t' * tabs +
            f'\\__CaseNode: case <expr> of [<case> ... <case>] esac',
            '\t' * (tabs + 1) + f'\\__case \n{expr} of',
        ]) + '\n' + cases

    @visitor.when(CallNode)
    def visit(self, node, tabs=0):
        obj = self.visit(node.obj, tabs + 1)
        ans = '\t' * tabs + f'\\__CallNode: <obj>.{node.id}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{obj}\n{args}'

    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__{node.__class__.__name__}: {node.lex}'

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__InstantiateNode: new {node.lex}()'

    @visitor.when(UnaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__}: <epxr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'
