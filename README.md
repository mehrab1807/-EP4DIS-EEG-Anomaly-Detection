# EP4DIS: Epileptic Seizure Detection Using Anomaly Detection Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Dataset: ds003029](https://img.shields.io/badge/Dataset-OpenNeuro%20ds003029-orange.svg)](https://openneuro.org/datasets/ds003029)

> **MSc Data Science & AI Dissertation Project**  
> Mehrab Jamil Shawon | 250372689 | Supervisor: Tony Dodd  
> Aston University, 2025–2026

## Overview

This project implements a **comparative anomaly detection framework** for epileptic seizure onset detection using clinical intracranial EEG (iEEG) data. We benchmark three mathematical models against clinician-verified seizure annotations from the OpenNeuro ds003029 dataset:

| Model | Type | Approach |
|-------|------|----------|
| **ARIMA** | Univariate | Autoregressive residual thresholding on single-channel time series |
| **ARMAX** | Multivariate | Extends ARIMA with exogenous spatial inputs from correlated neighbouring electrodes |
| **Kalman Filter** | Recursive Bayesian | State-space model using Expectation-Maximization for baseline learning |

## Dataset

**OpenNeuro ds003029** — Epilepsy-iEEG-Multicenter-Dataset

- **35 patients** across 4 clinical centres (Johns Hopkins, NIH, UMMC, UMF)
- **106 recording runs** with BrainVision format (.vhdr, .eeg, .vmrk)
- **27 clinician-verified seizure onset annotations**
- ~10.3 GB total (not included in this repository)

> **Associated Publication:** Li, A., et al. (2021) *"Neural Fragility as an EEG Marker of the Seizure Onset Zone."* Nature Neuroscience, 24(10), pp. 1465–1474.

### Downloading the Dataset

```bash
pip install openneuro-py
openneuro-py download --dataset ds003029 --target-dir data/
```

## Project Structure

```
EP4DIS-EEG-Anomaly-Detection/
├── api.py                          # FastAPI backend with analysis endpoints
├── main.py                         # Model comparison pipeline
├── preprocess.py                   # BIDS data loading & bandpass filtering
├── eda.py                          # 5-phase Exploratory Data Analysis
├── visualize.py                    # Matplotlib visualisation utilities
├── generate_dataset_pptx.py        # Presentation generator (18 slides)
├── models/
│   ├── arima_detector.py           # ARIMA anomaly detector
│   ├── armax_detector.py           # ARMAX anomaly detector
│   └── kalman_detector.py          # Kalman Filter anomaly detector
├── static/
│   └── index.html                  # Interactive web dashboard (Plotly.js)
├── eda_outputs/                    # Generated EDA visualisations
│   ├── 01_dataset_overview.png
│   ├── 02_raw_signal_5channels.png
│   ├── 03_spectral_analysis.png
│   ├── 04_seizure_vs_baseline.png
│   └── 05_channel_correlation.png
└── Dataset_Discussion_Presentation_v2.pptx
```

## Exploratory Data Analysis

Our EDA pipeline produces 5 publication-quality visualisations:

### 1. Dataset Overview
Subjects per clinical centre and recording runs per subject.

### 2. Raw Signal Inspection
First 5 iEEG channels plotted over 10 seconds at native sampling rate.

### 3. Power Spectral Density
Welch-method PSD across clinical EEG frequency bands (Delta, Theta, Alpha, Beta, Gamma).

### 4. Seizure vs Baseline Comparison
Side-by-side amplitude distributions, rolling variance, and PSD comparing interictal baseline against ictal onset.

### 5. Cross-Channel Correlation
Pearson correlation heatmap revealing 165 highly correlated electrode pairs (|r| > 0.7).

## Data Problems & Solutions

During EDA, we identified and resolved **8 data quality issues**:

| # | Problem | Solution |
|---|---------|----------|
| P1 | EVENT channel contains zero signal | Skip channel index 0 in preprocessing |
| P2 | Inconsistent sampling rates (499–1000 Hz) | Bandpass filter normalises frequency content |
| P3 | Only 27/106 runs have seizure annotations | Dynamic filtering to annotated files only |
| P4 | Channel naming varies across centres | Channel-agnostic numerical indexing |
| P5 | Extremely small amplitudes (10⁻⁴ V) | MNE handles unit scaling automatically |
| P6 | Variable channel counts (129–135) | Fixed-window epoching around onset |
| P7 | Download truncation corrupts files | File integrity validation |
| P8 | Missing 3D electrode coordinates | Correlation-based spatial proximity proxy |

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/EP4DIS-EEG-Anomaly-Detection.git
cd EP4DIS-EEG-Anomaly-Detection

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install mne numpy scipy statsmodels pykalman fastapi uvicorn matplotlib python-pptx
```

## Usage

### Run the EDA Pipeline
```bash
python eda.py
```

### Run the Model Comparison
```bash
python main.py
```

### Start the Web Dashboard
```bash
python api.py
# Open http://127.0.0.1:8000 in your browser
```

## Technologies

- **MNE-Python** — BrainVision iEEG data parsing
- **NumPy / SciPy** — Signal processing & spectral analysis
- **statsmodels** — ARIMA/ARMAX implementation
- **pykalman** — Kalman Filter with EM learning
- **FastAPI** — RESTful API backend
- **Plotly.js** — Interactive browser-based visualisation
- **Matplotlib** — Publication-quality static charts

## References

1. Li, A., et al. (2021). *Neural Fragility as an EEG Marker of the Seizure Onset Zone.* Nature Neuroscience, 24(10), 1465–1474.
2. Box, G.E.P., Jenkins, G.M. (1970). *Time Series Analysis: Forecasting and Control.* Holden-Day.
3. Kalman, R.E. (1960). *A New Approach to Linear Filtering and Prediction Problems.* Journal of Basic Engineering, 82(1), 35–45.
4. Shoeb, A.H. (2009). *Application of Machine Learning to Epileptic Seizure Onset Detection and Treatment.* MIT PhD Thesis.

## License

This project is part of an MSc dissertation at Aston University. The dataset is publicly available under the OpenNeuro Data Use Agreement.
