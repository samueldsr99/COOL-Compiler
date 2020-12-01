"""
Semantics Pipeline
"""
import streamlit as st

from core.semantics.collector import TypeCollector
from core.semantics.builder import TypeBuilder
from core.semantics.checker import TypeChecker
from core.semantics.inferer import TypeInferer
from core.semantics.formatter import FormatVisitor
from core.semantics.consistence import TypeConsistence


def check_semantics(ast, errors: list):
    formatter = FormatVisitor()
    print(formatter.visit(ast))

    # Collect types
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context

    # Build types
    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    # Checks for cycles in inheritance
    cons_checker = TypeConsistence(context, errors)
    cons_checker.visit(ast)

    # Infer Types
    inferer = TypeInferer(context, errors)

    scope, change = inferer.visit(ast)
    it = 1
    while change:
        print('repeating')
        print(change)
        scope, change = inferer.visit(ast)
        it += 1

    print('context', context)

    print(f'repetitions: {it}')
    # Check Types
<<<<<<< HEAD
    # st.subheader('checking types...')
    checker = TypeChecker(context, errors)
    #
=======
    st.subheader('checking types...')
    checker = TypeChecker(context, errors)

>>>>>>> e78ac0a0b25af7ef2af1ed6c3556c32fd5c1226b
    scope = checker.visit(ast, scope)

    formatter = FormatVisitor()
    output = formatter.visit(ast)

    st.text(output)
