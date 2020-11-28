from cmp.pycompiler import Grammar
from core.semantics.tools.cool_ast import *


G = Grammar()

# Non-Terminals
program = G.NonTerminal('<program>', startSymbol=True)
class_list, class_def = G.NonTerminals('<class-list> <class-def>')
feature_list = G.NonTerminal('<feature-list>')
attr_def, func_def = G.NonTerminals('<attr-def> <func-def>')
param_list = G.NonTerminal('<param-list>')
block = G.NonTerminal('<block>')
decl_list = G.NonTerminal('<decl-list>')
case_list = G.NonTerminal('<case-list>')
func_call = G.NonTerminal('<func-call>')
expr_list, not_void_expr_list, expr = G.NonTerminals('<expr-list> <not-void-expr-list> <expr>')
comp, arith, term, factor, atom = G.NonTerminals('<comp> <arith> <term> <factor> <atom>')

# Terminals
classx, elsex, fi, ifx, inx, inherits, isvoid, let, loop, pool = G.Terminals(
    'class else fi if in inherits isvoid let loop pool'
)
then, whilex, case, esac, new, of, notx, true, false = G.Terminals(
    'then while case esac new of not true false'
)
semi, colon, comma, dot, opar, cpar, ocur, ccur, assign, case_sign = G.Terminals(
    '; : , . ( ) { } <- =>'
)
plus, minus, star, div, less, less_eq, equal, int_comp, at = G.Terminals(
    '+ - * / < <= = ~ @'
)
idx, intx, typex, string = G.Terminals('id int type string')


# Productions
program %= class_list, lambda h,s: ProgramNode(s[1])

class_list %= class_def + class_list, lambda h,s: [s[1]] + s[2]
class_list %= class_def, lambda h,s: [s[1]]

class_def %= classx + typex + inherits + typex + ocur + feature_list + ccur + semi, lambda h,s: ClassDeclarationNode(s[2], s[6], s[4])
class_def %= classx + typex + ocur + feature_list + ccur + semi, lambda h,s: ClassDeclarationNode(s[2], s[4])

feature_list %= attr_def + semi + feature_list, lambda h,s: [s[1]] + s[3]
feature_list %= func_def + semi + feature_list, lambda h,s: [s[1]] + s[3]
feature_list %= G.Epsilon, lambda h, s: []

attr_def %= idx + colon + typex + assign + expr, lambda h,s: AttrDeclarationNode(s[1], s[3], s[5])
attr_def %= idx + colon + typex, lambda h, s: AttrDeclarationNode(s[1], s[3])

func_def %= idx + opar + param_list + cpar + colon + typex + ocur + not_void_expr_list + ccur, lambda h,s: FuncDeclarationNode(s[1], s[3], s[6], s[8])
func_def %= idx + opar + cpar + colon + typex + ocur + not_void_expr_list + ccur, lambda h,s: FuncDeclarationNode(s[1], [], s[5], s[7])

param_list %= idx + colon + typex + comma + param_list, lambda h,s: [(s[1], s[3])] + s[5]
param_list %= idx + colon + typex, lambda h,s: [(s[1], s[3])]

block %= expr + semi + block, lambda h,s: [s[1]] + s[3]
block %= expr + semi, lambda h,s: [s[1]]

decl_list %= idx + colon + typex + assign + expr + comma + decl_list, lambda h,s: [(s[1], s[3], s[5])] + s[7]
decl_list %= idx + colon + typex + comma + decl_list, lambda h,s: [(s[1], s[3], None)] + s[5]
decl_list %= idx + colon + typex + assign + expr, lambda h,s: [(s[1], s[3], s[5])]
decl_list %= idx + colon + typex, lambda h,s: [(s[1], s[3], None)]

case_list %= idx + colon + typex + case_sign + expr + semi + case_list, lambda h,s: [(s[1], s[3], s[5])] + s[7]
case_list %= idx + colon + typex + case_sign + expr, lambda h,s: [(s[1], s[3], s[5])]

func_call %= idx + opar + expr_list + cpar, lambda h,s: CallNode(s[1], s[3])
func_call %= atom + dot + idx + opar + expr_list + cpar, lambda h,s: CallNode(s[3], s[5], s[1])
func_call %= atom + at + typex + dot + idx + opar + expr_list + cpar, lambda h,s: CallNode(s[5], s[7], s[1], s[3])

expr_list %= not_void_expr_list, lambda h,s: s[1]
expr_list %= G.Epsilon, lambda h,s: []

not_void_expr_list %= expr + comma + not_void_expr_list, lambda h,s: [s[1]] + s[3]
not_void_expr_list %= expr, lambda h,s: [s[1]]

expr %= idx + assign + expr, lambda h,s: AssignNode(s[1], s[3])
expr %= ifx + expr + then + expr + elsex + expr + fi, lambda h,s: ConditionalNode(s[2], s[4], s[6])
expr %= whilex + expr + loop + expr + pool, lambda h,s: WhileNode(s[2], s[4])
expr %= ocur + block + ccur, lambda h,s: BlockNode(s[2])
expr %= let + decl_list + inx + expr, lambda h,s: LetNode(s[2], s[4])
expr %= case + expr + of + case_list + esac, lambda h,s: CaseNode(s[2], s[4])
expr %= notx + expr, lambda h,s: NegationNode(s[2])
expr %= comp, lambda h,s: s[1]

comp %= arith + less + arith, lambda h,s: LessThanNode(s[1], s[2], s[3])
comp %= arith + less_eq + arith, lambda h,s: LessEqualNode(s[1], s[2], s[3])
comp %= arith + equal + arith, lambda h,s: EqualNode(s[1], s[2], s[3])
comp %= arith, lambda h,s: s[1]

arith %= arith + plus + term, lambda h,s: PlusNode(s[1], s[2], s[3])
arith %= arith + minus + term, lambda h,s: MinusNode(s[1], s[2], s[3])
arith %= term, lambda h,s: s[1]

term %= term + star + factor, lambda h,s: StarNode(s[1], s[2], s[3])
term %= term + div + factor, lambda h,s: DivNode(s[1], s[2], s[3])
term %= factor, lambda h,s: s[1]

factor %= isvoid + factor, lambda h,s: IsVoidNode(s[2])
factor %= int_comp + factor, lambda h,s: ComplementNode(s[2])
factor %= atom, lambda h,s: s[1]

atom %= idx, lambda h, s: VariableNode(s[1])
atom %= intx, lambda h, s: IntegerNode(s[1])
atom %= string, lambda h, s: StringNode(s[1])
atom %= true, lambda h, s: BooleanNode(s[1])
atom %= false, lambda h, s: BooleanNode(s[1])
atom %= new + typex, lambda h, s: InstantiateNode(s[2])
atom %= func_call, lambda h, s: s[1]
atom %= opar + expr + cpar, lambda h, s: s[2]
# atom %= expr, lambda h, s: s[1]
