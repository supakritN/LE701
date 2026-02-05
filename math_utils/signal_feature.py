import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


# ============================================================
# Data models
# ============================================================

@dataclass(frozen=True)
class Point:
    """
    One point on the S21 curve (data-consistent).
    """
    f: float       # Frequency (GHz)
    s21: float     # S21 magnitude (dB)


@dataclass(frozen=True)
class Dip:
    """
    One resonance dip defined by its 3-dB bandwidth.
    """
    f1: Point      # Left 3-dB crossing
    f0: Point      # Resonance minimum (refined)
    f2: Point      # Right 3-dB crossing

    def bw(self) -> float:
        """3-dB bandwidth (GHz)"""
        bw = self.f2.f - self.f1.f
        if bw <= 0:
            raise ValueError("Invalid bandwidth")
        return bw

    def q(self) -> float:
        """Loaded Q-factor"""
        return self.f0.f / self.bw()

    def inv_q(self) -> float:
        """Inverse Q"""
        return 1.0 / self.q()


# ============================================================
# Internal helpers
# ============================================================

def _refine_minimum(freq, s21, idx) -> Point:
    """
    Parabolic interpolation to refine resonance minimum.
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
    Linear interpolation to find data-consistent 3-dB crossing.
    """
    if s2 == s1:
        return Point(f1, s1)

    ratio = (level - s1) / (s2 - s1)
    f = f1 + (f2 - f1) * ratio
    s = s1 + (s2 - s1) * ratio

    return Point(f, s)


def _find_3db_dip(
    freq: np.ndarray,
    s21: np.ndarray,
    idx: int,
    threshold_db: float
) -> Dip:
    """
    Extract a single resonance dip using refined f0 and interpolated 3-dB crossings.
    """
    # ---- refined minimum
    p0 = _refine_minimum(freq, s21, idx)
    level = p0.s21 + threshold_db

    # ---- left crossing (nearest)
    p1 = None
    for i in range(idx - 1, -1, -1):
        if s21[i] > level and s21[i + 1] <= level:
            p1 = _interp_point(
                freq[i], s21[i],
                freq[i + 1], s21[i + 1],
                level
            )
            break

    # ---- right crossing (nearest)
    p2 = None
    for i in range(idx + 1, len(freq)):
        if s21[i] > level and s21[i - 1] <= level:
            p2 = _interp_point(
                freq[i - 1], s21[i - 1],
                freq[i], s21[i],
                level
            )
            break

    if p1 is None or p2 is None or p2.f <= p1.f:
        raise ValueError("Invalid 3-dB dip")

    return Dip(
        f1=p1,
        f0=p0,
        f2=p2,
    )


def _is_valid_dip(
    dip: Dip,
    bw_max_ratio: float = 0.1,
    min_depth_db: float = 3.0,
    max_sym_ratio: float = 5.0,
) -> bool:
    """
    Physical validity checks for a resonance dip.
    """
    f0 = dip.f0.f
    f1 = dip.f1.f
    f2 = dip.f2.f

    if not (f1 < f0 < f2):
        return False

    bw = f2 - f1
    if bw <= 0:
        return False

    # ---- compact bandwidth (reject wide valleys)
    if bw / f0 > bw_max_ratio:
        return False

    # ---- dip depth check
    depth = dip.f1.s21 - dip.f0.s21
    if depth < min_depth_db:
        return False

    # ---- symmetry check
    left_bw = f0 - f1
    right_bw = f2 - f0
    sym_ratio = max(left_bw, right_bw) / min(left_bw, right_bw)
    if sym_ratio > max_sym_ratio:
        return False

    return True


# ============================================================
# Public API
# ============================================================

def extract_dips(
    data_points: List[Tuple[float, float]],
    threshold_db: float = 3.0,
    min_spacing: int = 5
) -> List[Dip]:
    """
    Extract all physically valid resonance dips.
    """
    if len(data_points) < 3:
        raise ValueError("Insufficient data points")

    freq = np.array([p[0] for p in data_points], dtype=float)
    s21 = np.array([p[1] for p in data_points], dtype=float)

    # ---- find local minima
    candidates = [
        i for i in range(1, len(s21) - 1)
        if s21[i] < s21[i - 1] and s21[i] < s21[i + 1]
    ]

    if not candidates:
        raise ValueError("No resonance dips found")

    # ---- deepest dips first
    candidates.sort(key=lambda i: s21[i])

    # ---- remove nearby duplicates
    selected = []
    for idx in candidates:
        if all(abs(idx - j) >= min_spacing for j in selected):
            selected.append(idx)

    dips: List[Dip] = []
    for idx in selected:
        try:
            dip = _find_3db_dip(freq, s21, idx, threshold_db)
            if _is_valid_dip(dip):
                dips.append(dip)
        except ValueError:
            continue

    if not dips:
        raise ValueError("No valid dips extracted")

    # ---- stable ordering (low f0 → high f0)
    dips.sort(key=lambda d: d.f0.f)

    return dips

