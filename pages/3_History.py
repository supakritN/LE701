import streamlit as st
from core.auth import require_login

require_login()

st.title("History")
st.info("History view will load past runs from db/results.")
