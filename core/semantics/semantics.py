"""
Semantics Pipeline
"""
from core.semantics.collector import TypeCollector
from core.semantics.builder import TypeBuilder
import streamlit as st


def check_semantics(ast, errors: list):
    # Collect types
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context

    # Build types
    builder = TypeBuilder(context, errors)

    builder.visit(ast)

    if errors:
        return -1

    st.text(context)
