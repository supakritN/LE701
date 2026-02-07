import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


# ============================================================
# Data models
# ============================================================

@dataclass(frozen=True)
class Point:
    f: float       # Frequency (GHz)
    s21: float     # S21 magnitude (dB)


@dataclass(frozen=True)
class Dip:
    f1: Point      # Left 3-dB crossing
    f0: Point      # Resonance minimum
    f2: Point      # Right 3-dB crossing

    def bw(self) -> float:
        return self.f2.f - self.f1.f

    def q(self) -> float:
        return self.f0.f / self.bw()

    def inv_q(self) -> float:
        return 1.0 / self.q()


# ============================================================
# Internal helpers
# ============================================================

def _refine_minimum(freq, s21, idx) -> Point:
    """Parabolic interpolation for f0"""
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
    """Linear interpolation to exact 3-dB level"""
    ratio = (level - s1) / (s2 - s1)
    f = f1 + (f2 - f1) * ratio
    return Point(f, level)


def _find_3db_dip(freq, s21, idx, threshold_db=3.0) -> Dip:
    # ---- refined frequency minimum
    p0 = _refine_minimum(freq, s21, idx)

    # ---- 3-dB level from RAW data (Excel reference)
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
        raise ValueError("3-dB crossings not found")

    return Dip(f1=p1, f0=p0, f2=p2)



# ============================================================
# Public API (n-band automatic)
# ============================================================

def extract_dips(
    data_points: List[Tuple[float, float]],
    threshold_db: float = 3.0,
    min_spacing: int = 3,
) -> List[Dip]:
    """
    Extract ALL resonance dips automatically (n-band),
    Excel / LE701 compatible.
    """
    freq = np.array([p[0] for p in data_points], dtype=float)
    s21 = np.array([p[1] for p in data_points], dtype=float)

    # ---- find all local minima
    candidates = [
        i for i in range(1, len(s21) - 1)
        if s21[i] < s21[i - 1] and s21[i] < s21[i + 1]
    ]

    if not candidates:
        return []

    # ---- sort by depth (deepest first)
    candidates.sort(key=lambda i: s21[i])

    # ---- remove duplicates that are too close
    selected = []
    for idx in candidates:
        if all(abs(idx - j) >= min_spacing for j in selected):
            selected.append(idx)

    dips: List[Dip] = []
    for idx in selected:
        try:
            dip = _find_3db_dip(freq, s21, idx, threshold_db)
            dips.append(dip)
        except ValueError:
            continue

    # ---- order by frequency (low → high)
    dips.sort(key=lambda d: d.f0.f)

    return dips
