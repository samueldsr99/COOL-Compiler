"""
Parsers & utils for parsers
"""

from core.utils.first_follow import (compute_firsts, compute_follows,
                                compute_local_first)


def build_parsing_table(G, firsts, follows):
    # init parsing table
    M = {}
    
    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right
        
        ###################################################
        # working with symbols on First(alpha) ...
        ###################################################
        #                   <CODE_HERE>                   #
        ###################################################    
        
        first = compute_local_first(firsts, alpha)
        
        for t in first:
            if M.get((X, t)):
                M[ (X, t) ].append(production)
            else:
                M[ (X, t) ] = [production]
        
        ###################################################
        # working with epsilon...
        ###################################################
        #                   <CODE_HERE>                   #
        ###################################################
    
        try:
            alpha_is_epsilon = alpha.IsEpsilon
        except:
            alpha_is_epsilon = False
        
        if alpha_is_epsilon:
            for t in follows[X]:
                if M.get((X, t)):
                    M[ (X, t) ].append(production)
                else:
                    M[ (X, t) ] = [production]
                
    
    # parsing table is ready!!!
    return M

def isLL1(G, M=None):
    if not M:
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)

    for cell in M:
        if len(M[cell]) > 1:
            return False
    return True

def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):

    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)
    
    
    # parser construction...
    def parser(w):
        
        ###################################################
        # w ends with $ (G.EOF)
        ###################################################
        # init:
        ### stack =  ????
        ### cursor = ????
        ### output = ????
        ###################################################
        stack = [G.startSymbol]
        cursor = 0
        output = []
        
        # parsing w...
        while len(stack) > 0 and cursor < len(w):
            top = stack.pop()
            a = w[cursor].token_type
    
            ###################################################
            #                   <CODE_HERE>                   #
            ###################################################

            nextToken = cursor
            
            if top.IsTerminal:
                nextToken += 1
                
                if a != top:
                    print(type(a), type(top))
                    # print(a, "!=", top)
                    print('a != top')
                    return False
            
            elif top.IsNonTerminal:
                if not M.get((top, w[nextToken].token_type)):
                    return False
                production = M[ (top, w[nextToken].token_type) ][0]
                prodRight = production.Right
                
                # if not production:
                #     return False
                
                output.append(production)
                
                for i in range(len(prodRight) - 1, -1, -1):
                    stack.append(prodRight[i])
                
            cursor = nextToken
        
        if len(stack) or cursor != len(w) - 1:
            # print("different size: ", len(stack), "!= 0 or", cursor, "!=", len(w))
            # print("the partial output is: ", output)
            print('130')
            return False
        # left parse is ready!!!
        return output
    
    # parser is ready!!!
    return parser
