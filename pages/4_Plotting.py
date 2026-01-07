import streamlit as st
from core.auth import require_login

require_login()

import matplotlib.pyplot as plt

st.title("Plotting")

files = st.session_state.get("files", [])

if not files:
    st.info("Upload files first.")
    st.stop()

f = st.selectbox("Select file", files, format_func=lambda x: x.display_name)

indep = f.independent_parameters()

plot_map = {}
for i, r in enumerate(f.results, 1):
    label = ", ".join(f"{k}={r.config[k]}" for k in indep) if indep else "fixed"
    plot_map[f"[{i}] {label}"] = r

selected = st.multiselect("Select results to plot", plot_map.keys())

if selected and st.button("Plot"):
    fig, ax = plt.subplots()

    for k in selected:
        r = plot_map[k]
        x, y = zip(*r.data)
        ax.plot(x, y, label=k)

    desc = f.results[0].description
    ax.set_xlabel(desc[0])
    ax.set_ylabel(desc[1])
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
