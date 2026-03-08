# Tidal Harmonic Analysis

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A clean Python workflow for tidal harmonic analysis using real BODC gauge data.
Demonstrated on **Avonmouth** (Bristol Channel, UK) — one of the highest tidal ranges in the world (~14 m spring range).

---

## Figure

![Harmonic Analysis](figures/fig_harmonic_analysis.png)

**(a)** 28-day tidal signal: gauge data vs 2, 8, and 12-constituent reconstructions.
**(b)** Residual (gauge − reconstructed): decreases markedly from 2 → 12 constituents.
**(c)** Tidal constituent amplitudes — M2 dominates at 4.29 m, reflecting the strong Bristol Channel resonance.
**(d)** NRMSE vs number of constituents — elbow around 12, diminishing returns beyond.

---

## Workflow

```
Raw BODC gauge data  (15-min interval, 8.3 years)
         │
         ▼
   Quality control          Remove flagged samples (N/M/T), de-mean
         │
         ▼
   Harmonic analysis        Fit 39 constituents via least squares (uptide)
         │
         ▼
   Signal reconstruction    Sum top-N constituent sinusoids
         │
         ▼
   NRMSE accuracy curve     Quantify reconstruction error vs N constituents
         │
         ▼
   fig_harmonic_analysis.png
```

---

## Project structure

```
tidal_analysis/
├── analyse.py          Entry point – runs the full workflow and saves the figure
├── core/
│   ├── io.py           BODC data loader and quality-control
│   ├── harmonic.py     Harmonic analysis and signal reconstruction (uptide)
│   └── metrics.py      Tidal energy metrics (PE, Hm0, tidal ranges)
├── figures/
│   └── fig_harmonic_analysis.png
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone git@github.com:pappas-k/Tidal-Harmonic-Analysis.git
cd Tidal-Harmonic-Analysis
pip install -r requirements.txt
```

---

## Usage

Place your BODC tidal gauge CSV at the path configured in `analyse.py` (default: `Avonmouth_20040101_20120430.csv`), then run:

```bash
python analyse.py
```

The figure is saved to `figures/fig_harmonic_analysis.png`.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [`uptide`](https://github.com/stephankramer/uptide) | Harmonic analysis and tidal reconstruction |
| `numpy` | Numerical arrays |
| `pandas` | Data handling |
| `scipy` | Peak detection |
| `matplotlib` | Plotting |

---

## Key results — Avonmouth (2004–2012)

Dominant constituent: **M2** (principal lunar semi-diurnal) at **4.29 m** amplitude, reflecting strong resonance in the Bristol Channel.

| Constituents | NRMSE |
|:---:|:---:|
| 1 | 0.436 |
| 2 | 0.283 |
| 4 | 0.208 |
| 8 | 0.147 |
| 12 | 0.129 |
| 30 | 0.108 |

---

## Data

Tide gauge records sourced from the [British Oceanographic Data Centre (BODC)](https://www.bodc.ac.uk/) — UK National Tide Gauge Network.

---

## Author

**Konstantinos Pappas** — PhD researcher in tidal energy resource assessment.
