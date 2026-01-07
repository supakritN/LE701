import streamlit as st
from core.auth import login, is_authenticated

st.set_page_config(page_title="Login", layout="wide")

# Hide sidebar BEFORE login
if not is_authenticated():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True
    )

# If already logged in, redirect to main page
if is_authenticated():
    st.switch_page("pages/1_Upload.py")

st.title("Login")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

    if submit:
        if login(username, password):
            st.success("Login successful")
            st.switch_page("pages/1_Upload.py")
        else:
            st.error("Invalid credentials")
