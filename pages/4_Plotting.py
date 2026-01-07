import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from core.auth import require_login
from rf_math.resonance import extract_dualband_resonances

require_login()

st.title("Plotting")
st.caption("S2,1 response with dual-band resonance annotation")

# ============================================================
# State
# ============================================================
files = st.session_state.get("files", [])

if not files:
    st.info("Upload files or restore a run first.")
    st.stop()

# ============================================================
# File selection
# ============================================================
f = st.selectbox(
    "Select file",
    files,
    format_func=lambda x: x.display_name
)

indep = f.independent_parameters()

# ============================================================
# Build plot map
# ============================================================
plot_map = {}
for i, r in enumerate(f.results, 1):
    param_label = (
        ", ".join(f"{k}={r.config[k]}" for k in indep)
        if indep else "fixed"
    )
    plot_map[f"[{i}] {param_label}"] = r

all_keys = list(plot_map.keys())

# ============================================================
# Default: select ALL
# ============================================================
selected = st.multiselect(
    "Select result(s) to plot",
    options=all_keys,
    default=all_keys
)

# ============================================================
# Plot + Download (IN-MEMORY ONLY)
# ============================================================
if selected and st.button("Plot"):
    fig, ax = plt.subplots(figsize=(8, 5))

    for key in selected:
        r = plot_map[key]

        freq = np.array([p[0] for p in r.data])
        s21 = np.array([p[1] for p in r.data])

        try:
            res = extract_dualband_resonances(freq, s21)

            label = (
                f"{key} | "
                f"Low={res['f_low']:.3f} GHz, "
                f"High={res['f_high']:.3f} GHz, "
                f"Main={res['f_res']:.3f} GHz"
            )
        except Exception:
            # Fallback if resonance extraction fails
            label = key

        ax.plot(freq, s21, label=label)

    # ---------- Axis labels ----------
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("S2,1 (dB)")
    ax.set_title(f.display_name)

    # ---------- Axis limits ----------
    ax.set_ylim(-45, 0)

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
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    safe_name = (
        f.display_name
        .replace(" ", "_")
        .replace(".txt", "")
    )

    st.download_button(
        label="⬇️ Download figure (PNG)",
        data=buf,
        file_name=f"{safe_name}_S21_plot.png",
        mime="image/png"
    )

    plt.close(fig)
