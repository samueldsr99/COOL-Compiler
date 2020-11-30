"""
Semantics Pipeline
"""
import streamlit as st

from core.semantics.collector import TypeCollector
from core.semantics.builder import TypeBuilder
from core.semantics.checker import TypeChecker
from core.semantics.inferer import TypeInferer
from core.semantics.formatter import FormatVisitor


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

    st.subheader('building types...')
    st.text(context)

    # Infer Types
    st.subheader('Infering types...')
    inferer = TypeInferer(context, errors)
    scope = inferer.visit(ast)
    st.text(str(scope))

    # Check Types
    # st.subheader('checking types...')
    # checker = TypeChecker(context, errors)
    #
    # scope = checker.visit(ast, scope)

    formatter = FormatVisitor()
    output = formatter.visit(ast)

    st.text(output)
