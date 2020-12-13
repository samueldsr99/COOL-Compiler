"""
Editor View
"""
import streamlit as st
from streamlit_ace import st_ace
from core.compiler import compile


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
    st.title(':memo: COOL Editor')

    code = st_ace(
        language='typescript',
        theme=st.sidebar.selectbox('Theme', options=THEMES, index=1),
        keybinding=st.sidebar.selectbox('Editor keymaps', options=KEYBINDINGS, index=3),
        font_size=st.sidebar.slider('Font size', 5, 24, 12),
        tab_size=4,
        show_gutter=st.sidebar.checkbox('Show gutter', value=True),
        show_print_margin=st.sidebar.checkbox('Show print margin', value=True),
        wrap=st.sidebar.checkbox('Wrap enabled', value=False),
        auto_update=False,
        key='ace-editor'
    )

    # compile code
    errors = []
    print('Compiling')
    result = compile(code, errors)

    if errors:
        st.text('\n'.join(error for error in errors))
