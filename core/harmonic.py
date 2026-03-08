"""
core/harmonic.py
Tidal harmonic analysis and signal reconstruction via the uptide library.
"""
import datetime
import numpy as np
import pandas as pd
import uptide


# 39 constituents considered in the analysis (diurnal, semi-diurnal, higher harmonics)
CONSTITUENTS = [
    "Q1", "O1", "P1", "S1", "K1", "J1", "M1",
    "2N2", "MU2", "N2", "NU2", "M2", "L2", "T2", "S2", "K2",
    "LAMBDA2", "EPS2", "R2", "ETA2", "MSN2", "MNS2", "3M2S2", "2SM2", "MKS2",
    "MK3", "MO3",
    "MS4", "MN4", "N4", "M4", "S4",
    "2MK6", "2MS6",
    "M3", "M5", "M6", "M7", "M8",
]


def harmonic_analysis(
    t: np.ndarray,
    eta: np.ndarray,
    start_date: datetime.datetime,
) -> pd.DataFrame:
    """Extract tidal harmonic constituents from a gauge record.

    Uses least-squares harmonic analysis (uptide).

    Parameters
    ----------
    t : np.ndarray
        Time in seconds since start_date.
    eta : np.ndarray
        Tidal elevation in metres (should be de-meaned).
    start_date : datetime.datetime
        Reference epoch matching t=0.

    Returns
    -------
    pd.DataFrame
        Columns: Constituent, Amplitude (m), Phase (rad).
        Sorted by amplitude in descending order.
    """
    tide = uptide.Tides(CONSTITUENTS)
    tide.set_initial_time(start_date)
    amplitudes, phases = uptide.analysis.harmonic_analysis(tide, eta, t)

    df = pd.DataFrame(
        {"Constituent": CONSTITUENTS, "Amplitude": amplitudes, "Phase": phases}
    )
    return df.sort_values("Amplitude", ascending=False, ignore_index=True)


def reconstruct(
    ha: pd.DataFrame,
    n_constituents: int,
    duration: float,
    start_date: datetime.datetime,
    dt: float = 108.0,
    t_start: float = 0.0,
):
    """Reconstruct a tidal signal from the top-n harmonic constituents.

    Parameters
    ----------
    ha : pd.DataFrame
        Output of harmonic_analysis(), sorted by amplitude.
    n_constituents : int
        Number of constituents to use (largest first).
    duration : float
        Signal length in seconds.
    start_date : datetime.datetime
        Reference epoch matching harmonic_analysis().
    dt : float
        Time step in seconds (default 108 s).
    t_start : float
        Start time offset from start_date in seconds.

    Returns
    -------
    t : np.ndarray
        Time array in seconds.
    eta : np.ndarray
        Reconstructed elevation in metres.
    """
    sub = ha.head(n_constituents)
    t   = np.arange(t_start, t_start + duration, dt)

    tide = uptide.Tides(list(sub["Constituent"]))
    tide.set_initial_time(start_date)
    eta = tide.from_amplitude_phase(
        sub["Amplitude"].values, sub["Phase"].values, t
    )
    return t, eta
