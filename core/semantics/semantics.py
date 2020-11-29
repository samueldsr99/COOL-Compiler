"""
Semantics Pipeline
"""
import streamlit as st

from core.semantics.collector import TypeCollector
from core.semantics.builder import TypeBuilder
from core.semantics.checker import TypeChecker


def check_semantics(ast, errors: list):
    # Collect types
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context

    # Build types
    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    st.text(context)

    # Check Types
    checker = TypeChecker(context, errors)

    scope = checker.visit(ast)

    st.text(scope.pprint())
