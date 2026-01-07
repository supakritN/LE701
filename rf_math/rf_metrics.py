from typing import Tuple, Optional, Dict
import numpy as np


# ============================================================
# Utility
# ============================================================

def apply_frequency_window(
    freq: np.ndarray,
    s21: np.ndarray,
    window: Tuple[float, float]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply a frequency window to the data.

    Parameters
    ----------
    freq : np.ndarray
        Frequency array (GHz)
    s21 : np.ndarray
        S21 array (dB)
    window : (f_min, f_max)
        Frequency window (GHz)

    Returns
    -------
    freq_win, s21_win
    """
    mask = (freq >= window[0]) & (freq <= window[1])
    return freq[mask], s21[mask]


# ============================================================
# Resonance detection
# ============================================================

def find_notch_resonance(
    freq: np.ndarray,
    s21: np.ndarray
) -> Tuple[float, float]:
    """
    Find notch-type resonance (minimum S21).

    Returns
    -------
    f0 : float
        Resonant frequency (GHz)
    s21_min : float
        Minimum S21 value (dB)
    """
    idx = int(np.argmin(s21))
    return float(freq[idx]), float(s21[idx])


# ============================================================
# Bandwidth calculation
# ============================================================

def bandwidth_minus_3db(
    freq: np.ndarray,
    s21: np.ndarray,
    f0: float,
    s21_min: float
) -> Optional[Tuple[float, float, float]]:
    """
    Calculate -3 dB bandwidth for a notch response.

    Bandwidth is measured relative to the minimum S21:
        S21 = S21_min + 3 dB

    Returns
    -------
    (f_low, f_high, bw) or None if invalid
    """
    level = s21_min + 3.0

    left_mask = (s21 <= level) & (freq < f0)
    right_mask = (s21 <= level) & (freq > f0)

    if not np.any(left_mask) or not np.any(right_mask):
        return None

    f_low = freq[left_mask].max()
    f_high = freq[right_mask].min()
    bw = f_high - f_low

    if bw <= 0:
        return None

    return float(f_low), float(f_high), float(bw)


# ============================================================
# Quality factor
# ============================================================

def quality_factor(f0: float, bw: float) -> float:
    """
    Compute quality factor.

    Q = f0 / BW
    """
    return float(f0 / bw)


# ============================================================
# Full analysis pipeline
# ============================================================

def analyze_notch_response(
    freq: np.ndarray,
    s21: np.ndarray,
    window: Tuple[float, float]
) -> Optional[Dict[str, float]]:
    """
    Perform full notch-response analysis.

    Steps
    -----
    1. Apply frequency window
    2. Find resonance (minimum S21)
    3. Compute -3 dB bandwidth
    4. Compute Q factor

    Returns
    -------
    dict with keys:
        - f0 : resonant frequency (GHz)
        - bw : bandwidth (GHz)
        - q  : quality factor
        - s21_min : minimum S21 (dB)

    or None if analysis fails.
    """

    # Windowing
    freq_w, s21_w = apply_frequency_window(freq, s21, window)

    if len(freq_w) < 5:
        return None

    # Resonance
    f0, s21_min = find_notch_resonance(freq_w, s21_w)

    # Bandwidth
    bw_result = bandwidth_minus_3db(freq_w, s21_w, f0, s21_min)
    if bw_result is None:
        return None

    _, _, bw = bw_result

    # Quality factor
    q = quality_factor(f0, bw)

    return {
        "f0": f0,
        "bw": bw,
        "q": q,
        "s21_min": s21_min
    }
