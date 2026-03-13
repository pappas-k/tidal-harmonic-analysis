# -*- coding: utf-8 -*-
"""
core/metrics.py
Tidal energy and variability metrics.

Metrics implemented
-------------------
PE      Depth-averaged tidal potential energy density  [Wh m⁻²]
Hm0     Significant tidal elevation: 4 × σ(η)         [m]
ranges  Individual tidal ranges from HW/LW extrema     [m]
monthly Monthly aggregates: PE, Hm0, P50, IQR(range)
"""
import datetime
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

RHO = 1021.0   # kg m⁻³  seawater density
G   = 9.81     # m s⁻²   gravitational acceleration


# ─────────────────────────────────────────────
# Scalar metrics
# ─────────────────────────────────────────────

def potential_energy(t: np.ndarray, eta: np.ndarray) -> float:
    """Time-averaged tidal potential energy density [Wh m⁻²].

    PE = (ρ g / Δt) ∫ η² dt
    """
    duration = t[-1] - t[0]
    return (RHO * G / duration) * np.trapz(eta ** 2, t) / 3600.0


def hm0(eta: np.ndarray) -> float:
    """Significant tidal elevation Hm0 = 4 σ(η) [m]."""
    return 4.0 * float(np.std(eta))


# ─────────────────────────────────────────────
# Tidal extrema
# ─────────────────────────────────────────────

def find_extrema(t: np.ndarray, eta: np.ndarray):
    """Return times and elevations of high-water (HW) and low-water (LW) peaks.

    Returns
    -------
    t_hw, eta_hw, t_lw, eta_lw : np.ndarray
    """
    hw_idx = find_peaks(eta)[0]
    lw_idx = find_peaks(-eta)[0]
    return t[hw_idx], eta[hw_idx], t[lw_idx], eta[lw_idx]


def mean_range(t_hw, eta_hw, t_lw, eta_lw) -> float:
    """Mean tidal range [m]."""
    return float(np.mean(tidal_ranges(t_hw, eta_hw, t_lw, eta_lw)))


def tidal_ranges(t_hw, eta_hw, t_lw, eta_lw) -> np.ndarray:
    """Compute tidal range for each successive HW–LW half-cycle.

    Merges extrema in chronological order and returns |Δη| for every
    alternating HW/LW pair.
    """
    times  = np.concatenate([t_hw,  t_lw])
    levels = np.concatenate([eta_hw, eta_lw])
    is_hw  = np.concatenate([np.ones(len(t_hw), bool), np.zeros(len(t_lw), bool)])

    order  = np.argsort(times)
    levels = levels[order]
    is_hw  = is_hw[order]

    ranges = [
        abs(levels[i + 1] - levels[i])
        for i in range(len(levels) - 1)
        if is_hw[i] != is_hw[i + 1]     # only alternating pairs
    ]
    return np.array(ranges)


# ─────────────────────────────────────────────
# Monthly aggregation
# ─────────────────────────────────────────────

def monthly_metrics(
    t: np.ndarray,
    eta: np.ndarray,
    start_date: datetime.datetime,
) -> pd.DataFrame:
    """Compute tidal metrics for each calendar month.

    Parameters
    ----------
    t : np.ndarray
        Time in seconds since start_date.
    eta : np.ndarray
        Tidal elevation in metres.
    start_date : datetime.datetime

    Returns
    -------
    pd.DataFrame  with columns: date, PE, Hm0, P50, IQR
    """
    dt_index = pd.to_datetime(start_date) + pd.to_timedelta(t, unit="s")
    years    = dt_index.year
    months   = dt_index.month

    records = []
    for y in np.unique(years):
        for m in np.unique(months[years == y]):
            mask  = (years == y) & (months == m)
            t_m   = t[mask]
            eta_m = eta[mask]

            if len(eta_m) < 50:
                continue

            t_hw, eta_hw, t_lw, eta_lw = find_extrema(t_m, eta_m)
            if len(t_hw) < 2 or len(t_lw) < 2:
                continue

            r = tidal_ranges(t_hw, eta_hw, t_lw, eta_lw)
            if len(r) == 0:
                continue

            records.append(
                {
                    "date": datetime.datetime(int(y), int(m), 15),
                    "PE":   potential_energy(t_m, eta_m),
                    "Hm0":  hm0(eta_m),
                    "P50":  float(np.percentile(r, 50)),
                    "IQR":  float(np.percentile(r, 75) - np.percentile(r, 25)),
                }
            )
    return pd.DataFrame(records)
