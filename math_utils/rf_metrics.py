from math_utils.signal_feature import Dip


# ============================================================
# RF metrics (LE701 reference)
# ============================================================

def window_size(dip1: Dip, dip2: Dip) -> float:
    """
    Inter-dip spacing (GHz)
    """
    return dip2.f0.f - dip1.f0.f


def frequency_shift_MHz(dip: Dip, f0_base: float) -> float:
    """
    Δf0 (MHz) = f0(er) − f0(er_base)
    """
    return (dip.f0.f - f0_base) * 1e3


def sensitivity(
    dip: Dip,
    f0_base: float,
    er: float,
    er_base: float = 1.0,
    norm: bool = True
) -> float:

    delta_er = er - er_base
    if delta_er == 0:
        return float("nan")
    
    sen = (abs(dip.f0.f - f0_base) / delta_er) * 100

    if norm:
        return sen / f0_base

    return sen
