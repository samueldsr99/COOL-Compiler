from cmp.pycompiler import EOF
G=iter
b=next
n=isinstance
D=None
K=len
F=enumerate
def evaluate_parse(productions, tokens):
	if not productions or not tokens:
		return
	productions=G(productions)
	tokens=G(tokens)
	x=evaluate(b(productions),productions,tokens)
	assert n(b(tokens).token_type,EOF)
	return x
def evaluate(production, productions, tokens,inherited_value=D):
	N,l=production
	y=production.attributes
	t=[D]*(K(l)+1)
	k=[D]*(K(l)+1)
	k[0]=inherited_value
	for i,R in F(l,1):
		if R.IsTerminal:
			assert k[i]is D
			t[i]=b(tokens).lex
		else:
			H=b(productions)
			assert R==H.Left
			P=y[i]
			if P is not D:
				k[i]=P(k,t)
			t[i]=evaluate(H,productions,tokens,k[i])
	P=y[0]
	return P(k,t)if P is not D else D

