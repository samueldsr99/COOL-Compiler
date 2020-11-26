"""
Editor View
"""
import streamlit as st
from streamlit_ace import st_ace

LANGUAGES = [
    'python',
    'csharp',
    'javascript',
    'typescript',
]

THEMES = [
    'ambiance', 'chaos', 'chrome', 'clouds', 'clouds_midnight', 'cobalt',
    'xcode', 'textmate', 'twilight', 'dracula'
]

KEYBINDINGS = [
    'emacs', 'sublime', 'vim', 'vscode'
]


def editor():
    st.title(':memo: Cool Editor')

    content = st_ace(
        language=st.sidebar.selectbox('Language mode', options=LANGUAGES, index=3),
        theme=st.sidebar.selectbox('Theme', options=THEMES, index=1),
        keybinding=st.sidebar.selectbox('Keybinding mode', options=KEYBINDINGS, index=3),
        font_size=st.sidebar.slider('Font size', 5, 24, 12),
        tab_size=st.sidebar.slider('Tab size', 1, 8, 4),
        show_gutter=st.sidebar.checkbox('Show gutter', value=True),
        show_print_margin=st.sidebar.checkbox('Show print margin', value=True),
        wrap=st.sidebar.checkbox('Wrap enabled', value=False),
        auto_update=st.sidebar.checkbox('Auto update', value=False),
        key='ace-editor'
    )

    st.code(content)
