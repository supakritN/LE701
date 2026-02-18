"""
signal_feature.py
Robust multi-band dip extraction for LE701
Pure NumPy version (no external libraries)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional


# ============================================================
# Data models
# ============================================================

@dataclass(frozen=True)
class Point:
    f: float        # Frequency (GHz)
    s21: float      # S21 magnitude (dB)


@dataclass(frozen=True)
class Dip:
    f1: Point       # Left 3-dB crossing
    f0: Point       # Resonance minimum
    f2: Point       # Right 3-dB crossing

    def bw(self) -> float:
        return self.f2.f - self.f1.f

    def q(self) -> float:
        bw = self.bw()
        return self.f0.f / bw if bw > 0 else np.nan

    def inv_q(self) -> float:
        q = self.q()
        return 1.0 / q if q > 0 else np.nan


# ============================================================
# Internal helpers
# ============================================================

def _refine_minimum(freq: np.ndarray, s21: np.ndarray, idx: int) -> Point:
    """
    Parabolic interpolation around local minimum
    """
    if idx <= 0 or idx >= len(freq) - 1:
        return Point(freq[idx], s21[idx])

    f1, f2, f3 = freq[idx - 1], freq[idx], freq[idx + 1]
    s1, s2, s3 = s21[idx - 1], s21[idx], s21[idx + 1]

    denom = (s1 - 2 * s2 + s3)
    if denom == 0:
        return Point(f2, s2)

    delta = (s1 - s3) / (2 * denom)
    f_min = f2 + delta * (f3 - f2)
    s_min = s2 - 0.25 * (s1 - s3) * delta

    return Point(f_min, s_min)


def _interp_point(f1, s1, f2, s2, level) -> Point:
    """
    Linear interpolation to exact crossing level
    """
    if s2 == s1:
        return Point(f1, level)

    ratio = (level - s1) / (s2 - s1)
    f = f1 + (f2 - f1) * ratio
    return Point(f, level)


def _validate_depth(s21: np.ndarray, idx: int, min_depth_db: float) -> bool:
    """
    10 dB buffer validation on both sides
    """
    s_min = s21[idx]

    if idx == 0 or idx == len(s21) - 1:
        return False

    left_max = np.max(s21[:idx])
    right_max = np.max(s21[idx+1:])

    return (
        (left_max - s_min) >= min_depth_db and
        (right_max - s_min) >= min_depth_db
    )


def _validate_slope(s21: np.ndarray, idx: int, min_slope_db: float) -> bool:
    """
    Ensure dip is not ripple (check slope at ±2 samples)
    """
    if idx < 2 or idx > len(s21) - 3:
        return False

    s_min = s21[idx]

    left_slope = s21[idx - 2] - s_min
    right_slope = s21[idx + 2] - s_min

    return (left_slope >= min_slope_db) and (right_slope >= min_slope_db)


def _find_3db_dip(
    freq: np.ndarray,
    s21: np.ndarray,
    idx: int,
    threshold_db: float
) -> Optional[Dip]:
    """
    Find exact 3-dB crossings around dip
    """

    p0 = _refine_minimum(freq, s21, idx)
    level = s21[idx] + threshold_db

    # ---- left crossing
    p1 = None
    for i in range(idx - 1, -1, -1):
        if s21[i] > level and s21[i + 1] <= level:
            p1 = _interp_point(
                freq[i], s21[i],
                freq[i + 1], s21[i + 1],
                level
            )
            break

    # ---- right crossing
    p2 = None
    for i in range(idx + 1, len(freq)):
        if s21[i] > level and s21[i - 1] <= level:
            p2 = _interp_point(
                freq[i - 1], s21[i - 1],
                freq[i], s21[i],
                level
            )
            break

    if p1 is None or p2 is None:
        return None

    return Dip(f1=p1, f0=p0, f2=p2)


# ============================================================
# Public API
# ============================================================

def extract_dips(
    data_points: List[Tuple[float, float]],
    threshold_db: float = 3.0,
    min_spacing: int = 5,
    min_depth_db: float = 10.0,
    min_slope_db: float = 0.5,
) -> List[Dip]:
    """
    Robust automatic multi-band dip extraction.

    Parameters
    ----------
    threshold_db : float
        3-dB bandwidth level (default = 3 dB)

    min_spacing : int
        Minimum sample spacing between dips

    min_depth_db : float
        Required dip depth (e.g. 10 dB buffer)

    min_slope_db : float
        Minimum slope requirement to avoid ripple

    Returns
    -------
    List[Dip]
    """

    if len(data_points) < 5:
        return []

    freq = np.array([p[0] for p in data_points], dtype=float)
    s21 = np.array([p[1] for p in data_points], dtype=float)

    # ---- detect local minima
    candidates = [
        i for i in range(1, len(s21) - 1)
        if s21[i] < s21[i - 1] and s21[i] < s21[i + 1]
    ]

    if not candidates:
        return []

    # ---- sort by depth (deepest first)
    candidates.sort(key=lambda i: s21[i])

    selected_indices = []
    dips: List[Dip] = []

    for idx in candidates:

        # spacing rule
        if any(abs(idx - j) < min_spacing for j in selected_indices):
            continue

        # edge reject
        if idx < 3 or idx > len(s21) - 4:
            continue

        # 10 dB buffer validation
        if not _validate_depth(s21, idx, min_depth_db):
            continue

        # slope validation
        if not _validate_slope(s21, idx, min_slope_db):
            continue

        dip = _find_3db_dip(freq, s21, idx, threshold_db)
        if dip is None:
            continue

        selected_indices.append(idx)
        dips.append(dip)

    # order by frequency
    dips.sort(key=lambda d: d.f0.f)

    return dips