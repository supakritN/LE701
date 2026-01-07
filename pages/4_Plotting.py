import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

from core.auth import require_login

require_login()

st.title("Plotting")

# =========================
# State
# =========================
files = st.session_state.get("files", [])

if not files:
    st.info("Upload files or restore a run first.")
    st.stop()

# =========================
# File selection
# =========================
f = st.selectbox(
    "Select file",
    files,
    format_func=lambda x: x.display_name
)

indep = f.independent_parameters()

# =========================
# Result selection
# =========================
plot_map = {}
for i, r in enumerate(f.results, 1):
    label = (
        ", ".join(f"{k}={r.config[k]}" for k in indep)
        if indep else "fixed"
    )
    plot_map[f"[{i}] {label}"] = r

selected = st.multiselect(
    "Select result(s) to plot",
    plot_map.keys()
)

# =========================
# Plot + Download (IN-MEMORY ONLY)
# =========================
if selected and st.button("Plot"):
    fig, ax = plt.subplots()

    for label in selected:
        r = plot_map[label]
        x, y = zip(*r.data)
        ax.plot(x, y, label=label)

    desc = f.results[0].description
    ax.set_xlabel(desc[0] if desc else "X")
    ax.set_ylabel(desc[1] if len(desc) > 1 else "Y")
    ax.set_title(f.display_name)
    ax.legend()
    ax.grid(True)

    # ---------- Show plot ----------
    st.pyplot(fig)

    # ---------- Prepare in-memory PNG ----------
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)

    safe_file = (
        f.display_name
        .replace(" ", "_")
        .replace(".txt", "")
    )
    file_name = f"{safe_file}_plot.png"

    st.download_button(
        label="⬇️ Download figure (PNG)",
        data=buf,
        file_name=file_name,
        mime="image/png"
    )

    plt.close(fig)

