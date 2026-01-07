import streamlit as st

APP_PASSWORD = "s21-analyzer"

st.set_page_config(
    page_title="S-Parameter Automation Tool",
    layout="wide"
)

st.title("Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

pwd = st.text_input("Password", type="password")

if st.button("Login"):
    if pwd == APP_PASSWORD:
        st.session_state.authenticated = True
        st.success("Login successful. Use the sidebar to navigate.")
        st.rerun()
    else:
        st.error("Invalid password")

if st.session_state.authenticated:
    st.info("Use the sidebar to continue.")

