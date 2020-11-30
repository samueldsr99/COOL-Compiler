from cmp.tools.parsing import metodo_predictivo_no_recursivo
from cmp.evaluation import evaluate
from .automata import NFA, DFA, nfa_to_dfa
from .automata import automata_union, automata_concatenation, automata_closure, automata_minimization
from cmp.pycompiler import Grammar
from cmp.utils import Token


class Node:
    def evaluate(self):
        raise NotImplementedError()

class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex

class UnaryNode(Node):
    def __init__(self, node):
        self.node = node

    def evaluate(self):
        value = self.node.evaluate()
        return self.operate(value)

    @staticmethod
    def operate(value):
        raise NotImplementedError()

class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        lvalue = self.left.evaluate()
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)

    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()


EPSILON = 'ε'

class EpsilonNode(AtomicNode):
    def evaluate(self):
        # Your code here!!!
        return DFA(states=1, finals=[0], transitions={})


class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        # Your code here!!!
        return DFA(states=2, finals=[1], transitions={(0, s): 1})


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_closure(value)


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_union(lvalue, rvalue)


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_concatenation(lvalue, rvalue)


def build_grammar():
    G = Grammar()

    E = G.NonTerminal('E', True)
    T, F, A, X, Y, Z = G.NonTerminals('T F A X Y Z')
    pipe, star, opar, cpar, symbol, epsilon = G.Terminals('| ^ [ ] symbol ε')

    # > PRODUCTIONS???
    # Your code here!!!
    E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]
    X %= pipe + E, lambda h, s: UnionNode(h[0], s[2])
    X %= G.Epsilon, lambda h, s: h[0]
    T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]
    Y %= T, lambda h, s: ConcatNode(h[0], s[1])
    Y %= G.Epsilon, lambda h, s: h[0]
    F %= A + Z, lambda h, s: s[2], None, lambda h, s: s[1]
    Z %= star, lambda h, s: ClosureNode(h[0])
    Z %= G.Epsilon, lambda h, s: h[0]
    A %= symbol, lambda h, s: SymbolNode(s[1])
    A %= epsilon, lambda h, s: EpsilonNode(s[1])
    A %= opar + E + cpar, lambda h, s: s[2]

    return G


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    # > fixed_tokens = ???
    # Your code here!!!
    fixed_tokens = {symbol: Token(symbol, G[symbol]) for symbol in ['|', '^', '[', ']', 'ε']}
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        # Your code here!!!
        try:
            actual = fixed_tokens[char]
        except KeyError:
            actual = Token(char, G['symbol'])
        tokens.append(actual)

    tokens.append(Token('$', G.EOF))
    return tokens


class Regex:

    def __init__(self, regex, skip_whitespaces=False):
        self.regex = regex
        self.automaton = self.build_automaton(regex)

    @staticmethod
    def build_automaton(regex, skip_whitespaces=False):
        G = build_grammar()
        tokens = regex_tokenizer(regex, G, skip_whitespaces=skip_whitespaces)
        parser = metodo_predictivo_no_recursivo(G)
        left_parse = parser(tokens)
        ast = evaluate(left_parse, tokens)
        dfa = nfa_to_dfa(ast.evaluate())
        return automata_minimization(dfa)


# regex = '[1|2][1|2]^'
# R = Regex(regex)
# text = ''
# print('all ok?', R.automaton.recognize(text))
