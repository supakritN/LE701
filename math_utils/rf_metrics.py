from math_utils.signal_feature import Dip


# ============================================================
# RF metrics
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
    shift_MHz: float,
    er: float,
    baseline_f0: float,
    er_base: float = 1.0,
    norm: bool = True,
) -> float:
    """
    Baseline-referenced sensitivity.

    Parameters
    ----------
    shift_MHz : float
        Δf0 in MHz
    er : float
        Relative permittivity
    baseline_f0 : float
        Baseline resonance frequency f0 (GHz)
    er_base : float, default 1.0
        Baseline permittivity
    norm : bool, default True
        If True, normalize by baseline f0:
            sen = sen / f0_base

    Returns
    -------
    float
        Sensitivity value (dimensionless), or NaN if undefined
    """
    delta_er = er - er_base
    if delta_er == 0:
        return float("nan")

    # |Δf0| / (er − er_base)
    sen = abs(shift_MHz) / delta_er

    # normalization by baseline resonance frequency
    if norm:
        sen = sen / baseline_f0

    # scale factor (Excel-compatible)
    return sen * (100 / 1000)
