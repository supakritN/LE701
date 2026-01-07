import numpy as np
from typing import Tuple, Optional, Dict


def _apply_window(freq: np.ndarray, s21: np.ndarray, window: Tuple[float, float]):
    mask = (freq >= window[0]) & (freq <= window[1])
    return freq[mask], s21[mask]


def _find_two_notches(freq: np.ndarray, s21: np.ndarray) -> Tuple[int, int]:
    """
    Find indices of the two deepest notches.
    Returned as (low_band_idx, high_band_idx)
    """
    idx_sorted = np.argsort(s21)
    i1, i2 = idx_sorted[0], idx_sorted[1]
    return (i1, i2) if freq[i1] < freq[i2] else (i2, i1)


def _bandwidth_3db(freq: np.ndarray, s21: np.ndarray, idx: int):
    f0 = freq[idx]
    smin = s21[idx]
    level = smin + 3.0

    left = freq[(s21 <= level) & (freq < f0)]
    right = freq[(s21 <= level) & (freq > f0)]

    if len(left) == 0 or len(right) == 0:
        return None

    f_low = left.max()
    f_high = right.min()
    bw = f_high - f_low

    if bw <= 0:
        return None

    return f0, bw, f0 / bw


def analyze_dualband_notch(
    freq: np.ndarray,
    s21: np.ndarray,
    window: Tuple[float, float]
) -> Optional[Dict[str, Dict[str, float]]]:
    """
    Dual-band notch analysis.
    Returns low-band and high-band metrics.
    """

    freq, s21 = _apply_window(freq, s21, window)

    if len(freq) < 10:
        return None

    idx_low, idx_high = _find_two_notches(freq, s21)

    low = _bandwidth_3db(freq, s21, idx_low)
    high = _bandwidth_3db(freq, s21, idx_high)

    if low is None or high is None:
        return None

    return {
        "low": {
            "f0": low[0],
            "bw": low[1],
            "Q": low[2],
        },
        "high": {
            "f0": high[0],
            "bw": high[1],
            "Q": high[2],
        }
    }
