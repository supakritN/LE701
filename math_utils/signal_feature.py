import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


# ============================================================
# Data models
# ============================================================

@dataclass(frozen=True)
class Point:
    """
    One point on the S21 curve.
    """
    f: float       # Frequency (GHz)
    s21: float     # S21 magnitude (dB)


@dataclass(frozen=True)
class Band:
    """
    One resonance band defined by 3-dB bandwidth.
    """
    f1: Point      # Left 3-dB crossing
    f0: Point      # Resonance (minimum S21)
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

def _find_3db_band(
    freq: np.ndarray,
    s21: np.ndarray,
    idx: int,
    threshold_db: float
) -> Band:
    """
    Extract a single resonance band using 3-dB rule.
    """
    f0_freq = freq[idx]
    s21_min = s21[idx]
    level = s21_min + threshold_db

    left = None
    for i in range(idx - 1, -1, -1):
        if s21[i] > level:
            left = i
            break

    right = None
    for i in range(idx + 1, len(freq)):
        if s21[i] > level:
            right = i
            break

    if left is None or right is None:
        raise ValueError("3-dB bounds not found")

    return Band(
        f1=Point(freq[left], s21[left]),
        f0=Point(f0_freq, s21_min),
        f2=Point(freq[right], s21[right]),
    )


# ============================================================
# Public API
# ============================================================

def extract_bands(
    data_points: List[Tuple[float, float]],
    threshold_db: float = 3.0,
    min_spacing: int = 5
) -> List[Band]:
    """
    Extract all resonance bands (Band 1 … Band N).
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

    bands: List[Band] = []
    for idx in selected:
        try:
            bands.append(_find_3db_band(freq, s21, idx, threshold_db))
        except ValueError:
            continue

    if not bands:
        raise ValueError("No valid bands extracted")

    # ---- stable ordering (low f0 → high f0)
    bands.sort(key=lambda b: b.f0.f)

    return bands
