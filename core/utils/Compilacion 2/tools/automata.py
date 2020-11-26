import pydot
from cmp.utils import ContainerSet, DisjointSet


class NFA:

    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass


class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        # Your code here
        try:
            self.current = self.transitions[self.current][symbol][0]
        except KeyError:
            return False
        return True
    
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        # Your code here
        self._reset()
        for symbol in string:
            if not self._move(symbol):
                return False
        return self.current in self.finals


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        # Your code here
        try:
            moves.update(set(automaton.transitions[state][symbol]))
        except KeyError:
            pass
    return moves


def epsilon_closure(automaton, states):
    pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
    closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
    
    while pending:
        state = pending.pop()
        # Your code here
        for x in automaton.epsilon_transitions(state):
            if x not in closure:
                closure.add(x)
                pending.append(x)
    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]

    pending = [ start ]
    while pending:
        state = pending.pop()
        
        for symbol in automaton.vocabulary:
            # Your code here
            # ...
            moves = move(automaton, state, symbol)
            e_closure = epsilon_closure(automaton, moves)
            if not e_closure:
                continue
            if e_closure not in states:
                e_closure.id = len(states)
                e_closure.is_final = any(s in automaton.finals for s in e_closure)
                states.append(e_closure)
                pending.append(e_closure)
            else:
                e_closure = states[states.index(e_closure)]
            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                # Your code here
                transitions[state.id, symbol] = e_closure.id
                pass
    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions)
    return dfa


def automata_union(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[origin + d1, symbol] = {dest + d1 for dest in destinations}

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[origin + d2, symbol] = {dest + d2 for dest in destinations}
    
    ## Add transitions from start state ...
    # Your code here
    transitions[start, ''] = [a1.start + d1, a2.start + d2]
    
    ## Add transitions to final state ...
    # Your code here
    for s, finals in zip([d1, d2], [a1.finals, a2.finals]):
        for f in finals:
            try:
                trans = transitions[f + s, '']
            except KeyError:
                trans = transitions[f + s, ''] = set()
            trans.add(final)
            
    states = a1.states + a2.states + 2
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[origin + d1, symbol] = {dest + d1 for dest in destinations}

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[origin + d2, symbol] = {dest + d2 for dest in destinations}
    
    ## Add transitions to final state ...
    # Your code here
    for f in a1.finals:
        try:
            trans = transitions[f + d1, '']
        except KeyError:
            trans = transitions[f + d1, ''] = set()
        trans.add(a2.start + d2)
    
    for f in a2.finals:
        try:
            trans = transitions[f + d2, '']
        except KeyError:
            trans = transitions[f + d2, ''] = set()
        trans.add(final)
    
            
    states = a1.states + a2.states + 1
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}
    
    start = 0
    d1 = 1
    final = a1.states + d1
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        # Your code here
        transitions[origin + d1, symbol] = {dest + d1 for dest in destinations}
    
    ## Add transitions from start state ...
    # Your code here
    transitions[start, ''] = [a1.start + d1, final]
    
    ## Add transitions to final state and to start state ...
    # Your code here
    for f in a1.finals:
        try:
            trans = transitions[f + d1, '']
        except KeyError:
            trans = transitions[f + d1, ''] = set()
        trans.add(final)
        trans.add(a1.start + d1)
            
    states = a1.states +  2
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        # Your code here
        trans = automaton.transitions[member.value]
        nodes = ((trans[symbol][0] if symbol in trans else None) for symbol in vocabulary)
        rep = tuple((partition[node].representative if node in partition.nodes else None) for node in nodes)
        try:
            split[rep].append(member.value)
        except KeyError:
            split[rep] = [member.value]

    return [ group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))
    
    ## partition = { NON-FINALS | FINALS }
    # Your code here
    partition.merge(f for f in automaton.finals)
    partition.merge(s for s in range(automaton.states) if s not in automaton.finals)
    
    while True:
        new_partition = DisjointSet(*range(automaton.states))
        
        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        # Your code here
        for group in partition.groups:
            for states in distinguish_states(group, automaton, partition):
                new_partition.merge(states)

        if len(new_partition) == len(partition):
            break

        partition = new_partition
        
    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)
    
    states = [s for s in partition.representatives]
    
    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        # Your code here
        origin = state.value
        for symbol, destinations in automaton.transitions[origin].items():
            # Your code here
            r = partition[destinations[0]].representative
            index = states.index(r)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                # Your code here
                transitions[i, symbol] = index
    
    ## finals = ???
    ## start  = ???
    # Your code here
    finals = [i for i, state in enumerate(states) if state.value in automaton.finals]
    start = states.index(partition[automaton.start].representative)
    
    return DFA(len(states), finals, transitions, start)