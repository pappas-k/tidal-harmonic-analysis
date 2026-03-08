# -*- coding: utf-8 -*-
"""
core/io.py
Load and quality-control BODC tidal gauge data.

BODC CSV format (15-minute interval):
    - 2 header lines
    - Column 11: tidal elevation (m)
    - Column 12: QC flag  ('N'=error, 'M'=missing, 'T'=suspect)
"""
import datetime
import numpy as np
import pandas as pd


def load_bodc(filepath: str, start_date: datetime.datetime):
    """Load a BODC tidal gauge CSV and return quality-controlled (t, eta).

    Parameters
    ----------
    filepath : str
        Path to the BODC CSV file.
    start_date : datetime.datetime
        Epoch; t=0 corresponds to this date.

    Returns
    -------
    t : np.ndarray
        Time in seconds since start_date (non-uniform after QC).
    eta : np.ndarray
        De-meaned tidal elevation in metres.
    """
    n_rows = sum(1 for _ in open(filepath)) - 2          # data rows only
    t_raw = np.arange(0, n_rows * 15 * 60, 15 * 60)      # uniform 15-min grid

    eta_raw = np.loadtxt(filepath, skiprows=2, usecols=(11,), dtype=float, delimiter=",")
    qc_raw  = np.loadtxt(filepath, skiprows=2, usecols=(12,), dtype=str,   delimiter=",")

    df = pd.DataFrame({"t": t_raw, "eta": eta_raw, "qc": qc_raw})

    # Drop flagged samples and physically implausible values
    bad = df["qc"].str.contains("N|M|T", regex=True)
    df  = df[~bad & (df["eta"] > -15) & (df["eta"] < 15)].copy()

    t   = df["t"].values
    eta = df["eta"].values - df["eta"].mean()     # remove mean water level
    return t, eta
