import streamlit as st

def set_state_defaults(**kwargs):
    for k,v in kwargs.items():
        if k not in st.session_state:
            st.session_state[k]=v
