# EP4DIS: Epileptic Seizure Detection Using Anomaly Detection Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Dataset: ds003029](https://img.shields.io/badge/Dataset-OpenNeuro%20ds003029-orange.svg)](https://openneuro.org/datasets/ds003029)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![MNE](https://img.shields.io/badge/EEG-MNE--Python-blue.svg)](https://mne.tools/)

> **MSc Data Science & AI Dissertation Project**  
> Mehrab Jamil Shawon | 250372689 | Supervisor: Tony Dodd  
> Aston University, 2025–2026

---

## 🧠 Overview

This project implements a **comparative anomaly detection framework** for epileptic seizure onset detection using clinical intracranial EEG (iEEG) data. We benchmark three mathematical models against clinician-verified seizure annotations from the OpenNeuro ds003029 dataset:

| Model | Type | Approach |
|-------|------|----------|
| **ARIMA** | Univariate | Autoregressive residual thresholding on single-channel time series |
| **ARMAX** | Multivariate | Extends ARIMA with exogenous spatial inputs from correlated neighbouring electrodes |
| **Kalman Filter** | Recursive Bayesian | State-space model using Expectation-Maximization for baseline learning |

---

## 🏆 Key Achievements

| Achievement | Detail |
|-------------|--------|
| **5-Phase EDA Pipeline** | Automated exploratory analysis covering dataset overview, raw signal inspection, spectral PSD, seizure vs baseline comparison, and cross-channel spatial correlation |
| **8 Data Problems Resolved** | Systematically identified and solved 8 real-world data quality issues including inconsistent sampling rates, zero-signal hardware channels, and missing electrode coordinates |
| **165 Correlated Channel Pairs** | Discovered 165 electrode pairs with Pearson r > 0.7, empirically justifying the ARMAX exogenous spatial input methodology |
| **Full-Stack Web Dashboard** | Built an interactive FastAPI + Plotly.js web application for real-time model comparison and EEG signal visualisation |
| **3 Model Implementations** | Production-ready ARIMA, ARMAX, and Kalman Filter anomaly detectors with standardised interfaces for benchmarking |
| **Publication-Quality Outputs** | 5 research-grade visualisations, 18-slide academic presentation, and a comprehensive project report — all auto-generated from code |
| **35-Patient Clinical Dataset** | Processed 10.3 GB of multicenter iEEG data (106 recording runs) from 4 clinical centres using BIDS-compliant pipelines |
| **Delta-Band Dominance Validated** | Confirmed elevated 0.5–4 Hz power in epileptogenic tissue, aligning with published clinical literature |

---

## 🔧 Technologies Used

### Core Data Science & Signal Processing
| Technology | Purpose | Why It Matters |
|-----------|---------|----------------|
| **Python 3.11** | Primary language | Industry-standard for data science & ML |
| **NumPy** | Numerical computing | Array operations, statistical calculations, matrix algebra |
| **SciPy** | Scientific computing | Welch PSD estimation, bandpass filtering (Butterworth), signal processing |
| **Pandas** | Data manipulation | Parsing BIDS event files (.tsv), tabular data handling |

### Machine Learning & Statistical Modelling
| Technology | Purpose | Why It Matters |
|-----------|---------|----------------|
| **statsmodels** | ARIMA / ARMAX | Time-series autoregressive models with exogenous variable support |
| **pykalman** | Kalman Filter | Recursive Bayesian state-space estimation with EM-based parameter learning |
| **Matplotlib** | Static visualisation | Publication-quality EDA charts with custom dark theme styling |

### Neuroscience & EEG
| Technology | Purpose | Why It Matters |
|-----------|---------|----------------|
| **MNE-Python** | EEG data parsing | Reads BrainVision (.vhdr/.eeg/.vmrk) files, handles electrode metadata |
| **OpenNeuro** | Dataset source | Standardised BIDS-iEEG clinical data repository |
| **BIDS Format** | Data structure | Brain Imaging Data Structure — international standard for neuroimaging |

### Web Application & API
| Technology | Purpose | Why It Matters |
|-----------|---------|----------------|
| **FastAPI** | Backend REST API | High-performance async endpoints for model inference and data serving |
| **Uvicorn** | ASGI server | Production-grade async web server |
| **Plotly.js** | Interactive charts | Browser-based zoomable/pannable EEG signal visualisation |
| **HTML5 / CSS3 / JavaScript** | Frontend | Responsive dark-theme web dashboard with glassmorphism design |

### DevOps & Reporting
| Technology | Purpose | Why It Matters |
|-----------|---------|----------------|
| **Git / GitHub** | Version control | Full commit history, code collaboration, portfolio hosting |
| **python-pptx** | Presentation generation | Auto-generates 18-slide academic presentations from code |
| **lxml** | XML manipulation | PowerPoint transparency overlays via direct XML editing |

---

## 📊 Dataset

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

---

## 📁 Project Structure

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
│   ├── index.html                  # Interactive web dashboard
│   ├── styles.css                  # Dark-theme CSS with glassmorphism
│   └── app.js                      # Plotly.js chart rendering logic
├── eda_outputs/                    # Generated EDA visualisations
│   ├── 01_dataset_overview.png
│   ├── 02_raw_signal_5channels.png
│   ├── 03_spectral_analysis.png
│   ├── 04_seizure_vs_baseline.png
│   └── 05_channel_correlation.png
└── Dataset_Discussion_Presentation_v2.pptx
```

---

## 🔬 Exploratory Data Analysis

Our EDA pipeline produces 5 publication-quality visualisations:

### Phase 1: Dataset Overview
Subjects per clinical centre and recording runs per subject.

### Phase 2: Raw Signal Inspection
First 5 iEEG channels plotted over 10 seconds at native sampling rate (499–1000 Hz).

### Phase 3: Power Spectral Density
Welch-method PSD across clinical EEG frequency bands (Delta, Theta, Alpha, Beta, Gamma). **Finding:** Delta-band (0.5–4 Hz) dominates, confirming epileptogenic tissue characteristics.

### Phase 4: Seizure vs Baseline Comparison
Side-by-side amplitude distributions, rolling variance, and PSD comparing interictal baseline against ictal onset. **Finding:** Ictal variance dramatically exceeds baseline — validating Kalman Filter's state-transition detection approach.

### Phase 5: Cross-Channel Correlation
Pearson correlation heatmap revealing **165 highly correlated electrode pairs (|r| > 0.7)**, justifying ARMAX's spatial modelling approach.

---

## ⚠️ Data Problems & Solutions

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

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/mehrab1807/-EP4DIS-EEG-Anomaly-Detection.git
cd -EP4DIS-EEG-Anomaly-Detection

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

---

## 📚 References

1. Li, A., et al. (2021). *Neural Fragility as an EEG Marker of the Seizure Onset Zone.* Nature Neuroscience, 24(10), 1465–1474.
2. Box, G.E.P., Jenkins, G.M. (1970). *Time Series Analysis: Forecasting and Control.* Holden-Day.
3. Kalman, R.E. (1960). *A New Approach to Linear Filtering and Prediction Problems.* Journal of Basic Engineering, 82(1), 35–45.
4. Shoeb, A.H. (2009). *Application of Machine Learning to Epileptic Seizure Onset Detection and Treatment.* MIT PhD Thesis.
5. Durbin, J., Koopman, S.J. (2012). *Time Series Analysis by State Space Methods.* Oxford University Press.

---

## License

This project is part of an MSc dissertation at Aston University. The dataset is publicly available under the OpenNeuro Data Use Agreement.

---

<p align="center">
  <b>Built with ❤️ for clinical neuroscience research</b><br>
  <sub>Aston University | MSc Data Science & AI | 2025–2026</sub>
</p>
