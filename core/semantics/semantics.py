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

    # st.subheader('building types...')

    # Infer Types
    # st.subheader('Infering types...')
    inferer = TypeInferer(context, errors)

    scope, change = inferer.visit(ast)
    it = 1
    while change:
        print('repeating')
        print(scope, change)
        scope, change = inferer.visit(ast)
        it += 1

    print(f'repetitions: {it}')
    # Check Types
    # st.subheader('checking types...')
    checker = TypeChecker(context, errors)
    #
    scope = checker.visit(ast, scope)

    formatter = FormatVisitor()
    output = formatter.visit(ast)

    st.text(output)
