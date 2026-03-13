# -*- coding: utf-8 -*-
"""
analyse.py
Tidal Harmonic Analysis

Demonstrates a full tidal harmonic analysis workflow on real BODC gauge data
(Avonmouth, UK – one of the highest tidal ranges in the world):

  1. Load & quality-control raw gauge data
  2. Harmonic analysis → tidal constituent table
  3. Signal reconstruction with increasing numbers of constituents
  4. NRMSE accuracy curve

Figure produced
---------------
figures/fig_harmonic_analysis.png

Usage
-----
    python3 analyse.py
"""
import datetime
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import numpy as np

from core.io       import load_bodc
from core.harmonic import harmonic_analysis, reconstruct


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DATA_FILE  = Path("../tidal_signal_5/inputs/BODC_tidal_elevation_data/"
                  "Avonmouth_20040101_20120430.csv")
START_DATE = datetime.datetime(2004, 1, 1)
LOCATION   = "Avonmouth"
LAT, LON   = 51.5109, -2.7150

FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

DT          = 108.0                                          # reconstruction time-step [s]
N_PLOT      = [2, 4, 8, 12]                                  # constituents shown in signal comparison
N_SCAN      = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30] # NRMSE curve
WINDOW_DAYS = 28                                             # days of signal shown in panel (a)

# ─────────────────────────────────────────────────────────────────────────────
# Style
# ─────────────────────────────────────────────────────────────────────────────

plt.rcParams.update(
    {
        "font.family":       "sans-serif",
        "font.size":         11,
        "axes.labelsize":    12,
        "axes.titlesize":    12,
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "legend.fontsize":   9.5,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "figure.dpi":        150,
    }
)

GAUGE_COL = "#1a2a5e"           # dark navy – gauge data
CON_COLS  = {                   # reconstruction colours
    2:  "#e8a838",
    4:  "#e05c3a",
    8:  "#27ae60",
    12: "#6a0dad",
}


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── 1. Load data ──────────────────────────────────────────────────────────
    print(f"Loading {LOCATION} tide gauge data …")
    t, eta = load_bodc(str(DATA_FILE), START_DATE)
    years  = (t[-1] - t[0]) / (365.25 * 86400)
    print(f"  {len(t):,} observations after QC  ({years:.1f} years)")

    # ── 2. Harmonic analysis ──────────────────────────────────────────────────
    print("Performing harmonic analysis …")
    ha = harmonic_analysis(t, eta, START_DATE)
    print("\nTop 12 constituents:")
    print(ha.head(12).to_string(index=False))
    print()

    # ── 3. Reconstruct signals for plotting ───────────────────────────────────
    print("Reconstructing signals …")
    t_start  = float(t[0])
    duration = float(t[-1] - t[0])

    reconstructions = {}
    for n in N_PLOT:
        t_r, eta_r = reconstruct(ha, n, duration, START_DATE, dt=DT, t_start=t_start)
        reconstructions[n] = (t_r, eta_r)

    # ── 4. NRMSE accuracy scan ─────────────────────────────────────────────────
    print("Computing NRMSE curve …")
    sigma_gauge = float(np.std(eta))
    nrmse_scan  = {}
    for n in N_SCAN:
        if n > len(ha):
            break
        t_r, eta_r    = reconstruct(ha, n, duration, START_DATE, dt=DT, t_start=t_start)
        eta_i         = np.interp(t, t_r, eta_r)
        nrmse_scan[n] = float(np.sqrt(np.mean((eta - eta_i) ** 2))) / sigma_gauge
        print(f"  {n:2d} cons. → NRMSE = {nrmse_scan[n]:.4f}")

    nrmse_12       = nrmse_scan.get(12, float("nan"))
    var_explained  = (1.0 - nrmse_12 ** 2) * 100
    print(f"  Variance explained (12 cons.): {var_explained:.1f}%")

    # ── 5. Tidal regime (Munk-Cartwright form factor) ─────────────────────────
    ff = _form_factor(ha)
    if   ff < 0.25: regime = "semi-diurnal"
    elif ff < 1.5:  regime = "mixed, predominantly semi-diurnal"
    elif ff < 3.0:  regime = "mixed, predominantly diurnal"
    else:           regime = "diurnal"
    print(f"\nForm factor  F = (K1+O1)/(M2+S2) = {ff:.4f}  →  {regime}")

    # ── 6. Plot ────────────────────────────────────────────────────────────────
    print("\nPlotting …")
    _fig_harmonic_analysis(t, eta, ha, reconstructions, nrmse_scan)
    print(f"Figure saved to {FIG_DIR}/")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _form_factor(ha):
    """Munk-Cartwright tidal form factor F = (K1 + O1) / (M2 + S2).

    Classifies tidal regime:
        F < 0.25        semi-diurnal
        0.25 <= F < 1.5 mixed, predominantly semi-diurnal
        1.5  <= F < 3.0 mixed, predominantly diurnal
        F >= 3.0        diurnal
    """
    def amp(name):
        row = ha[ha["Constituent"] == name]
        return float(row["Amplitude"].values[0]) if len(row) else 0.0

    k1, o1 = amp("K1"), amp("O1")
    m2, s2 = amp("M2"), amp("S2")
    return (k1 + o1) / (m2 + s2) if (m2 + s2) > 0 else float("nan")


# ─────────────────────────────────────────────────────────────────────────────
# Figure – Harmonic analysis
# ─────────────────────────────────────────────────────────────────────────────

def _fig_harmonic_analysis(t, eta, ha, reconstructions, nrmse_scan):
    """Four-panel figure: signal comparison · residuals · amplitudes · NRMSE."""

    fig = plt.figure(figsize=(13, 10))
    gs  = gridspec.GridSpec(
        3, 2, figure=fig,
        height_ratios=[1.5, 1.0, 1.8],
        hspace=0.55, wspace=0.40,
    )
    ax_sig = fig.add_subplot(gs[0, :])    # (a) signal – full width
    ax_res = fig.add_subplot(gs[1, :])    # (b) residuals – full width
    ax_amp = fig.add_subplot(gs[2, 0])    # (c) constituent amplitudes
    ax_err = fig.add_subplot(gs[2, 1])    # (d) NRMSE curve

    # Metadata banner
    fig.text(
        0.01, 0.995,
        f"Location: {LOCATION}  |  Lat {LAT:.4f}°N  Lon {abs(LON):.4f}°W"
        f"  |  Source: BODC",
        fontsize=9, color="grey", va="top",
    )

    # ── Window: first 28 days ─────────────────────────────────────────────────
    window = WINDOW_DAYS * 86400
    t_mask = t <= t[0] + window
    t_w    = t[t_mask]
    eta_w  = eta[t_mask]
    t_days = (t_w - t_w[0]) / 86400

    # ── (a) Signal comparison ──────────────────────────────────────────────────
    ax_sig.plot(t_days, eta_w, color=GAUGE_COL, lw=0.9, label="Gauge data", zorder=6)
    for n in [2, 8, 12]:
        t_r, eta_r = reconstructions[n]
        r_mask     = (t_r >= t_w[0]) & (t_r <= t_w[-1])
        t_r_days   = (t_r[r_mask] - t_w[0]) / 86400
        ax_sig.plot(t_r_days, eta_r[r_mask],
                    color=CON_COLS[n], lw=1.1, alpha=0.9,
                    label=f"{n} constituents", zorder=5)

    ax_sig.axhline(0, color="grey", lw=0.5, ls="--")
    ax_sig.set_xlim(0, WINDOW_DAYS)
    ax_sig.set_xlabel("Time (days)")
    ax_sig.set_ylabel("η (m)")
    ax_sig.legend(loc="upper left", ncol=2, framealpha=1.0)
    ax_sig.set_title(
        f"(a) Tidal signal reconstruction — {LOCATION}",
        loc="left", fontweight="bold",
    )

    # Key stats annotation
    m2_amp   = float(ha[ha["Constituent"] == "M2"]["Amplitude"].values[0])
    nrmse_12 = nrmse_scan.get(12, float("nan"))
    ax_sig.text(
        0.995, 0.04,
        f"M2 = {m2_amp:.2f} m   |   NRMSE (12 cons.) = {nrmse_12:.3f}",
        transform=ax_sig.transAxes, fontsize=9, color="#444444",
        ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75,
                  edgecolor="lightgrey"),
    )

    # ── (b) Residuals ──────────────────────────────────────────────────────────
    for n in [2, 8, 12]:
        t_r, eta_r = reconstructions[n]
        eta_i      = np.interp(t_w, t_r, eta_r)
        ax_res.plot(t_days, eta_w - eta_i,
                    color=CON_COLS[n], lw=0.8, alpha=0.85,
                    label=f"{n} cons.")

    ax_res.axhline(0, color="grey", lw=0.6, ls="--")
    ax_res.set_xlim(0, WINDOW_DAYS)
    ax_res.set_xlabel("Time (days)")
    ax_res.set_ylabel("Residual η (m)")
    ax_res.legend(loc="upper right", ncol=3, framealpha=0.7)
    ax_res.set_title(
        "(b) Gauge minus reconstructed signal",
        loc="left", fontweight="bold",
    )

    # ── (c) Constituent amplitudes ─────────────────────────────────────────────
    top_n = 15
    sub   = ha.head(top_n)
    y_pos = np.arange(top_n)

    bars = ax_amp.barh(y_pos, sub["Amplitude"], color=GAUGE_COL, alpha=0.82)
    for bar in bars[:12]:
        bar.set_alpha(0.90)
    for bar in bars[12:]:
        bar.set_alpha(0.40)

    ax_amp.set_yticks(y_pos)
    ax_amp.set_yticklabels(sub["Constituent"], fontsize=9)
    ax_amp.invert_yaxis()
    ax_amp.set_xlabel("Amplitude (m)")
    ax_amp.xaxis.grid(True, alpha=0.25, ls="--", zorder=0)
    ax_amp.set_title("(c) Constituent amplitudes (top 15)", loc="left", fontweight="bold")
    ax_amp.text(
        0.97, 0.05, "Darker = used in reconstruction",
        transform=ax_amp.transAxes, fontsize=8, color="grey",
        ha="right", va="bottom",
    )

    # ── (d) NRMSE curve ────────────────────────────────────────────────────────
    n_vals     = sorted(nrmse_scan)
    nrmse_vals = [nrmse_scan[n] for n in n_vals]

    ax_err.plot(n_vals, nrmse_vals, "o-", color="#c0392b", lw=1.6, ms=5, zorder=5)
    ax_err.axvline(12, color=CON_COLS[12], lw=1.0, ls="--", alpha=0.7, label="12 cons.")
    ax_err.set_xlabel("Number of constituents")
    ax_err.set_ylabel("NRMSE")
    ax_err.set_xticks(n_vals)
    ax_err.tick_params(axis="x", labelrotation=45)
    ax_err.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.3f"))
    ax_err.legend(fontsize=9)
    ax_err.yaxis.grid(True, alpha=0.25, ls="--", zorder=0)
    ax_err.set_title("(d) Reconstruction accuracy", loc="left", fontweight="bold")

    fig.savefig(FIG_DIR / "fig_harmonic_analysis.png", dpi=500, bbox_inches="tight")
    plt.close(fig)
    print("  Saved fig_harmonic_analysis.png")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
