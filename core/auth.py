import streamlit as st


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def login(username: str, password: str) -> bool:
    # Simple placeholder auth
    if username == "admin" and password == "Le7012026":
        st.session_state["authenticated"] = True
        return True
    return False


def require_login():
    if not is_authenticated():
        st.switch_page("web_app.py")
