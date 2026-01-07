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
# Result mapping
# =========================
plot_map = {}
for i, r in enumerate(f.results, 1):
    label = (
        ", ".join(f"{k}={r.config[k]}" for k in indep)
        if indep else "fixed"
    )
    plot_map[f"[{i}] {label}"] = r

all_keys = list(plot_map.keys())

# =========================
# Default: select ALL
# =========================
selected = st.multiselect(
    "Select result(s) to plot",
    options=all_keys,
    default=all_keys
)

# =========================
# Plot + Download (IN-MEMORY ONLY)
# =========================
if selected and st.button("Plot"):
    fig, ax = plt.subplots(figsize=(8, 5))

    for label in selected:
        r = plot_map[label]

        # Original data format: (frequency, s21)
        freq, s21 = zip(*r.data)

        ax.plot(freq, s21, label=label)

    # ---------- Axis labels ----------
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("S2,1 (dB)")
    ax.set_title(f.display_name)

    # ---------- Axis limits (BORDER) ----------
    ax.set_xlim(1.0, 7.0)
    ax.set_ylim(-45.0, 0.0)

    # ---------- Legend outside ----------
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0
    )

    ax.grid(True)

    # ---------- Render ----------
    st.pyplot(fig, clear_figure=True)

    # ---------- In-memory download ----------
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)

    safe_file = (
        f.display_name
        .replace(" ", "_")
        .replace(".txt", "")
    )

    st.download_button(
        label="⬇️ Download figure (PNG)",
        data=buf,
        file_name=f"{safe_file}_plot.png",
        mime="image/png"
    )

    plt.close(fig)
