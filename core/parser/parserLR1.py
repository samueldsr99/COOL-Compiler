from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from core.utils.first_follow import compute_firsts, compute_local_first
from cmp.automata import State, multiline_formatter
from .parserSR import ShiftReduceParser


def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()
    # Your code here!!! (Compute lookahead for child items)
    for string in item.Preview():
        lookaheads.update(compute_local_first(firsts, string))

    assert not lookaheads.contains_epsilon
    # Your code here!!! (Build and return child items)
    return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]


def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return {Item(x.production, x.pos, set(lookahead))
            for x, lookahead in centers.items()}


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)

    changed = True
    while changed:
        changed = False

        new_items = ContainerSet()
        # Your code here!!!
        for item in closure:
            new_items.extend(expand(item, firsts))

        changed = closure.update(new_items)

    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            # Your code here!!! (Get/Build `next_state`)
            closure = closure_lr1(current, firsts)
            goto = frozenset(goto_lr1(closure, symbol, just_kernel=True))
            if not goto:
                continue
            try:
                next_state = visited[goto]
            except KeyError:
                closure = closure_lr1(goto, firsts)
                next_state = visited[goto] = State(frozenset(closure), True)
                pending.append(goto)
            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), (self.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    goto_id = node.get(next_symbol.Name).idx
                    if next_symbol.IsTerminal:
                        self._register(self.action, (idx, next_symbol), (self.SHIFT, goto_id))
                    else:
                        self._register(self.goto, (idx, next_symbol), goto_id)

    @staticmethod
    def _register(table, key, value):
        if key in table and table[key] != value:
            raise Exception('Shift-Reduce or Reduce-Reduce conflict!!!')
        table[key] = value
