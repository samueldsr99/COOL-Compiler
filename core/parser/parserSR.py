
class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w, errors: list):
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor].token_type

            if self.verbose:
                print(stack, '<---||--->', w[cursor:])

            # Your code here!!! (Detect error)
            if (state, lookahead) not in self.action:
                print(type(lookahead))
                errors.append(f'ParsingError: Error in state {state}, lookahead {lookahead}.')
                return None

            action, tag = self.action[state, lookahead]
            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                cursor += 1
                stack += [lookahead, tag]
                print('SHIFTING ', lookahead, tag)
            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                output.append(tag)
                left, right = tag
                for symbol in reversed(right):
                    stack.pop()
                    print(f'{stack[-1], type(stack[-1])}, {symbol.Name, type(symbol.Name)}')
                    assert stack.pop() == symbol.Name, f'Parsing Error in Reduce case: {tag}'
                state = stack[-1]
                goto = self.goto[state, left.Name]
                stack += [left.Name, goto]
                print('REDUCE ', left, right)
            # Your code here!!! (OK case)
            elif action == self.OK:
                stack.pop()
                assert stack.pop() == self.G.startSymbol.Name, 'Parsing error in OK case'
                assert len(stack) == 1, 'Error: parsing ended with symbols in stack.'
                print('OK')
                return output
            # Your code here!!! (Invalid case)
            else:
                raise Exception('Error: Wrong action.')
