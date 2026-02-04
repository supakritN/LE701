from math_utils.signal_feature import Band


# ============================================================
# RF metrics
# ============================================================

def window_size(band1: Band, band2: Band) -> float:
    """
    Inter-band spacing (GHz)
    """
    return band2.f0.f - band1.f0.f


def frequency_shift_MHz(band: Band, f0_base: float) -> float:
    """
    Δf0 (MHz) = f0(er) − f0(er_base)
    """
    return (band.f0.f - f0_base) * 1e3


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
    er_base : float, default 1.0
        Baseline permittivity
    norm : bool, default True
        If True, apply εr normalization:
            sen = sen / er

    Returns
    -------
    float
        Sensitivity value (MHz/εr), or NaN if undefined
    """
    delta_er = er - er_base
    if delta_er == 0:
        return float("nan")

    sen = abs(shift_MHz) / delta_er

    if norm:
        sen = sen / baseline_f0

    return sen * (100/1000)
