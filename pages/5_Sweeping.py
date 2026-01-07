import streamlit as st
from core.auth import require_login

require_login()

st.title("Sweeping")
st.info("Parameter sweeping analysis will be implemented here.")
