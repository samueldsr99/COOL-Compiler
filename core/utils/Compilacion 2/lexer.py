from tools.regex import Regex
from cmp.utils import Token
from cmp.automata import State


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
    
    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            # Your code here!!!
            # - Remember to tag the final states with the token_type and priority.
            # - <State>.tag might be useful for that purpose ;-)
            regex_aut, regex_aut_states= State.from_nfa(Regex(regex).automaton, get_states=True)
            for state in regex_aut_states:
                if state.final:
                    state.tag = (token_type, n)
            regexs.append(regex_aut)
        return regexs
    
    def _build_automaton(self):
        start = State('start')
        # Your code here!!!
        for aut in self.regexs:
            start.add_epsilon_transition(aut)
        
        return start.to_deterministic()
        
    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''
            
        for symbol in string:
            # Your code here!!!
            if symbol in state.transitions:  # exists transition for symbol
                state = state.transitions[symbol][0]
                lex += symbol
                if state.final:
                    final = state
                    final_lex = lex
            else:
                break
        return final, final_lex
    
    def _tokenize(self, text):
        # Your code here!!!
        processed = 0
        while processed < len(text):
            final, final_lex = self._walk(text[processed:])    # get actual state and lex
            if final is None or len(final_lex) == 0:
                raise Exception(f'Invalid token at position {processed + 1}: "{text[processed]}"')
            processed += len(final_lex)
            pos_ret = []
            for s in final.state:
                if s.tag is not None:
                    pos_ret.append(s)
            ret = pos_ret[0]
            for i in range(1, len(pos_ret)):
                if pos_ret[i].tag[1] < ret.tag[1]:
                    ret = pos_ret[i]
            yield final_lex, ret.tag[0]

        yield '$', self.eof
    
    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]