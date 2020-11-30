"""
Index View
"""
import streamlit as st

from views.editor import editor


def main():
    options = [
        'Inicio',
        'Editor',
    ]

    choice = st.sidebar.selectbox('', options, index=1)

    if choice == options[0]:
        try:
            with open('./INTRODUCTION.md', 'r') as fd:
                st.markdown(fd.read())
        except FileNotFoundError:
            st.error('El archivo INTRODUCTION.md no existe')
    if choice == options[1]:
        editor()


if __name__ == '__main__':
    main()
