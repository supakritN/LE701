import numpy as np
from typing import List, Tuple


def find_peak(
    data_points: List[Tuple[float, float]],
    threshold_db: float = 3.0
) -> Tuple[float, float, float]:
    """
    Find resonance peak and -3 dB bounds.

    Parameters
    ----------
    data_points : [(freq, s21)]
        Assumed ordered by frequency
    threshold_db : float
        dB level above minimum for bandwidth

    Returns
    -------
    (f1, fres, f2)
    """

    freq = np.array([p[0] for p in data_points])
    s21 = np.array([p[1] for p in data_points])

    # deepest notch
    idx = int(np.argmin(s21))
    fres = freq[idx]
    smin = s21[idx]
    level = smin + threshold_db

    # left bound
    f1 = None
    for i in range(idx - 1, -1, -1):
        if s21[i] > level:
            f1 = freq[i]
            break

    # right bound
    f2 = None
    for i in range(idx + 1, len(freq)):
        if s21[i] > level:
            f2 = freq[i]
            break

    if f1 is None or f2 is None:
        raise ValueError("Bandwidth bounds not found")

    return float(f1), float(fres), float(f2)


def get_low_band(
    data_points: List[Tuple[float, float]],
    scope: float = 4.0
) -> Tuple[float, float, float]:
    """
    Low band: from start to scope frequency.
    """
    scoped = [p for p in data_points if p[0] <= scope]

    if len(scoped) < 3:
        raise ValueError("Insufficient points in low-band scope")

    return find_peak(scoped)


def get_high_band(
    data_points: List[Tuple[float, float]],
    scope: float = 4.0
) -> Tuple[float, float, float]:
    """
    High band: from scope frequency to end.
    """
    scoped = [p for p in data_points if p[0] >= scope]

    if len(scoped) < 3:
        raise ValueError("Insufficient points in high-band scope")

    return find_peak(scoped)
