"""
Preprocessed Lexer
"""
import re
from cmp.utils import Token


class Lexer:

    def __init__(self):
        self.eof = '$'
        self.keywords = (
            'class', 'else', 'fi', 'if', 'in', 'inherits', 'isvoid', 'let',
            'loop', 'pool', 'then', 'while', 'case', 'esac', 'new', 'of', 'not'
        )
        self.symbols = (
            '<-', '+', '-', '/', '*', '~', '(', ')', '@', ',',
            '<', '<=', '=>', '=', ':', '.', ';', '{', '}'
        )
        self.table = self._build_table()

    def _build_table(self):
        table: dict[str, re.Pattern] = {}
        
        for keyword in self.keywords:
            table[keyword] = re.compile(f'^{keyword}', re.IGNORECASE)

        table['true'] = re.compile('t[rR][uU][eE]')
        table['false'] = re.compile('f[fF][aA][lL][sS][eE]')

        for symbol in self.symbols:
            table[symbol] = re.compile(symbol)

        # Use fullmatch to get the string
        # Stops when finds a "
        table['string'] = re.compile('(^(\\"|\\\n|[^"\n])*)')

        table['space'] = re.compile('\s+')

        table['type'] = re.compile('[A-Z]\w*')

        table['id'] = re.compile('[a-z]\w*')

        table['line_comm'] = re.compile('--.*\n')

        return table
  

    def __call__(self, code: str, errors: list):
        """
        :code: - string of COOL code for tokenize.
        """
        line = 1
        col = 1
        tokens = []

        while len(code) > 0:

            if code.startswith('"'):  # Next token should be string
                col += 1
                lex = '"'
                pos = lambda : len(lex)
                open_string = True
                while len(lex) < len(code):
                    if code[pos()] == '\\':
                        try:
                            if code[pos() + 1] == '0':
                                lex += '\\0'
                                col += 2
                                errors.append(f'{(col, line)} LexicographicError: Strings cannot contain "\\0".')
                            elif code[pos() + 1] == '"':
                                lex += '\\"'
                                col += 2
                            elif code[pos() + 1] == '\n':
                                lex += '\\\n'
                                line += 1
                                col = 1
                        except KeyError:
                            col += 1
                            errors.append(f'{(col, line)} LexicographicError: Unterminated string.')
                    elif code[pos()] == '\n':
                        lex += '\n'
                        col = 1
                        line += 1
                        errors.append(f'{(col, line)} LexicographicError: String cannot contain not escaped new line.')
                    elif code[pos()] == '"':
                        lex += '"'
                        col += 1
                        tokens.append(Token(lex=lex, token_type='string'))
                        open_string = False
                        break
                if open_string:
                    errors.append(f'{(col, line)} LexicographicError: Unterminated string.')
                code = code[pos():]

            elif code.startswith('(*'):  # Next is a comment
                stack = ['(*']
                col += 2

                while



            elif code.startswith('--'):


if __name__ == "__main__":
    code = """class B{
    s : String <- "Hello";
    g (y:String) : Int {
        y.concat(s)
    };
    f (x:Int) : Int {
        x+1
    };
};

class A inherits B {
    a : Int;
    b : B <- new B;
    f(x:Int) : Int {
        x+a
    };
};"""

lexer = Lexer()
x = re.match(lexer.table['class'], code)
print(x)
# print(lexer(code))
