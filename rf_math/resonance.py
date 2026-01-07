import numpy as np
from typing import Dict


def extract_dualband_resonances(
    freq: np.ndarray,
    s21: np.ndarray
) -> Dict[str, float]:
    """
    Extract dual-band resonance information from S21 curve.

    Returns
    -------
    {
        "f_low": float,   # lower-frequency notch
        "s21_low": float,
        "f_high": float,  # higher-frequency notch
        "s21_high": float,
        "f_res": float    # deeper (main) resonance
    }
    """

    if len(freq) < 5:
        raise ValueError("Insufficient data points")

    idx = np.argsort(s21)

    i1, i2 = idx[0], idx[1]

    # Order by frequency
    if freq[i1] < freq[i2]:
        f_low, f_high = freq[i1], freq[i2]
        s_low, s_high = s21[i1], s21[i2]
    else:
        f_low, f_high = freq[i2], freq[i1]
        s_low, s_high = s21[i2], s21[i1]

    # Main resonance = deeper notch
    f_res = f_low if s_low < s_high else f_high

    return {
        "f_low": float(f_low),
        "s21_low": float(s_low),
        "f_high": float(f_high),
        "s21_high": float(s_high),
        "f_res": float(f_res),
    }
