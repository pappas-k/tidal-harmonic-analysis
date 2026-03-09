# Tidal Harmonic Analysis

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A clean Python workflow for tidal harmonic analysis using real BODC gauge data.
Demonstrated on **Avonmouth** (Bristol Channel, UK) — one of the highest tidal ranges in the world (~14 m spring range).

---

## Figure

![Harmonic Analysis](figures/fig_harmonic_analysis.png)

**(a)** 28-day tidal signal: gauge data vs 2, 8, and 12-constituent reconstructions. Spring-neap modulation (~14-day period) is clearly visible.
**(b)** Residual (gauge − reconstructed): 2-constituent errors exceed 1 m; 12-constituent residuals are substantially smaller.
**(c)** Tidal constituent amplitudes — M2 dominates at 4.29 m, driven by resonance in the Bristol Channel funnel geometry.
**(d)** NRMSE vs number of constituents — sharp improvement up to ~12, then diminishing returns.

> The spring-neap cycle (~14 days) in panel (a) arises from the constructive/destructive interference of M2 and S2.

---

## Method

Tidal harmonic analysis decomposes the sea-surface elevation into a sum of sinusoidal components (constituents), each with a known astronomical frequency:

$$\eta(t) = \sum_{i} A_i \cos(\omega_i t - \phi_i)$$

where $A_i$ is the amplitude, $\omega_i$ the angular frequency, and $\phi_i$ the phase lag of constituent $i$. Amplitudes and phases are estimated from the gauge record by least-squares fitting using the [`uptide`](https://github.com/stephankramer/uptide) library.

**39 constituents** are fitted, spanning four frequency bands:

| Band | Period | Key constituents |
|------|--------|-----------------|
| Diurnal | ~24 h | K1, O1, P1, Q1 |
| Semi-diurnal | ~12 h | **M2**, S2, N2, K2 |
| Compound / overtides | ~6–8 h | M4, MS4, MK3 |
| Higher harmonics | ~4 h and above | M6, M8 |

The reconstructed signal uses the top-N constituents ranked by amplitude. NRMSE (normalised by the standard deviation of the gauge record) quantifies reconstruction accuracy as a function of N.

---

## Site: Avonmouth

Avonmouth sits at the mouth of the Bristol Channel, which acts as a natural funnel that amplifies the oceanic tide through resonance. The Bristol Channel has the **second highest tidal range in the world** (~14 m spring range), exceeded only by the Bay of Fundy, Canada.

| Property | Value |
|----------|-------|
| Location | 51.51°N, 2.71°W |
| Mean spring range | ~12.3 m |
| Mean neap range | ~6.5 m |
| Dominant constituent | M2 — amplitude 4.29 m |
| Data period | Jan 2004 – Apr 2012 (8.3 years) |
| Source | BODC UK National Tide Gauge Network |

---

## Workflow

```
Raw BODC gauge data  (15-min interval, 8.3 years)
         │
         ▼
   Quality control          Remove flagged samples (N / M / T flags), de-mean
         │
         ▼
   Harmonic analysis        Fit 39 constituents via least squares  [uptide]
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
├── analyse.py          Entry point — runs the full workflow and saves the figure
├── core/
│   ├── io.py           BODC data loader and quality-control
│   ├── harmonic.py     Harmonic analysis and signal reconstruction (uptide)
│   └── metrics.py      Tidal energy metrics: PE, Hm0, tidal ranges, IQR
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

Set the `DATA_FILE` and `START_DATE` in `analyse.py` to point to your BODC gauge CSV, then run:

```bash
python3 analyse.py
```

The figure is saved to `figures/fig_harmonic_analysis.png`.

---

## Key results — Avonmouth (2004–2012)

Dominant constituent: **M2** (principal lunar semi-diurnal, period 12.42 h) at **4.29 m** amplitude — more than twice the next largest constituent (S2 at 1.53 m). This strong M2 dominance is characteristic of macrotidal sites with near-resonant basin geometry.

Reconstruction accuracy improves rapidly with the number of constituents:

| Constituents | NRMSE | Improvement vs previous |
|:---:|:---:|:---:|
| 1 | 0.436 | — |
| 2 | 0.283 | −35% |
| 4 | 0.208 | −26% |
| 8 | 0.147 | −29% |
| 12 | 0.129 | −12% |
| 30 | 0.108 | −16% |

12 constituents capture the bulk of tidal energy; the remaining error is primarily due to non-tidal (meteorological) variability not resolvable by harmonic methods.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [`uptide`](https://github.com/stephankramer/uptide) | Tidal harmonic analysis and reconstruction |
| `numpy` | Numerical arrays |
| `pandas` | Data handling |
| `scipy` | Peak detection (`find_peaks`) |
| `matplotlib` | Plotting |

---

## Data

Tide gauge records sourced from the [British Oceanographic Data Centre (BODC)](https://www.bodc.ac.uk/) — UK National Tide Gauge Network.

---

## Author

**Konstantinos Pappas** — PhD researcher in tidal energy resource assessment.
GitHub: [pappas-k](https://github.com/pappas-k)
