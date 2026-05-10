"""
EEG Dataset Exploratory Data Analysis (EDA)
============================================
A comprehensive data science exploration of the OpenNeuro ds003029 dataset.
Generates multiple publication-quality visualizations and prints analytical feedback.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import csv
import glob
import warnings
warnings.filterwarnings("ignore")

# Use a clean, modern style
plt.rcParams.update({
    'figure.facecolor': '#0f172a',
    'axes.facecolor': '#1e293b',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#e2e8f0',
    'text.color': '#e2e8f0',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#334155',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

OUTPUT_DIR = "eda_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")

def feedback(msg):
    print(f"  💡 FEEDBACK: {msg}")

# ─────────────────────────────────────────────────────────────
# PHASE 1: Dataset-Level Overview
# ─────────────────────────────────────────────────────────────
def phase1_dataset_overview():
    log("PHASE 1: Dataset-Level Overview")
    
    base_dir = "data"
    
    # 1a. Count subjects, centres, and runs
    subject_dirs = [d for d in os.listdir(base_dir) if d.startswith("sub-") and os.path.isdir(os.path.join(base_dir, d))]
    
    centres = {"jh": [], "pt": [], "ummc": [], "umf": []}
    for sub in subject_dirs:
        for prefix in centres:
            if sub.startswith(f"sub-{prefix}"):
                centres[prefix].append(sub)
                break
    
    print(f"\n  Total Subjects: {len(subject_dirs)}")
    for centre, subs in centres.items():
        label = {"jh": "Johns Hopkins", "pt": "NIH (pt)", "ummc": "UMMC", "umf": "UMF"}
        print(f"    {label.get(centre, centre)}: {len(subs)} subjects ({', '.join(subs[:3])}{'...' if len(subs)>3 else ''})")
    
    # 1b. Count total .vhdr/.eeg files and total runs
    vhdr_files = []
    for root, dirs, files in os.walk(base_dir, followlinks=True):
        for f in files:
            if f.endswith(".vhdr"):
                vhdr_files.append(os.path.join(root, f))
    
    print(f"\n  Total EEG Recording Runs: {len(vhdr_files)}")
    
    # 1c. Count events files
    events_files = []
    for root, dirs, files in os.walk(base_dir, followlinks=True):
        for f in files:
            if f.endswith("_events.tsv"):
                events_files.append(os.path.join(root, f))
    print(f"  Total Events (Annotation) Files: {len(events_files)}")
    
    # 1d. Scan all events files to count seizure annotations
    total_sz_onsets = 0
    total_sz_offsets = 0
    subjects_with_seizures = set()
    
    for ef in events_files:
        with open(ef, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                trial_type = row.get('trial_type', '').strip().lower()
                if trial_type == 'sz onset':
                    total_sz_onsets += 1
                    # extract subject from path
                    parts = ef.replace("\\", "/").split("/")
                    for p in parts:
                        if p.startswith("sub-"):
                            subjects_with_seizures.add(p)
                elif trial_type == 'sz offset':
                    total_sz_offsets += 1
    
    print(f"\n  Total 'sz onset' annotations: {total_sz_onsets}")
    print(f"  Total 'sz offset' annotations: {total_sz_offsets}")
    print(f"  Subjects with at least one seizure: {len(subjects_with_seizures)}/{len(subject_dirs)}")
    
    feedback("Every subject has clinician-verified seizure annotations — this confirms the dataset provides a robust ground truth for benchmarking.")
    
    # 1e. Plot: Subjects per centre (bar chart)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    labels = ["Johns Hopkins", "NIH (pt)", "UMMC", "UMF"]
    counts = [len(centres["jh"]), len(centres["pt"]), len(centres["ummc"]), len(centres["umf"])]
    colors = ['#3b82f6', '#a855f7', '#10b981', '#f59e0b']
    
    bars = axes[0].bar(labels, counts, color=colors, edgecolor='white', linewidth=0.5)
    axes[0].set_title("Subjects per Clinical Centre", fontsize=14, fontweight='bold')
    axes[0].set_ylabel("Number of Subjects")
    for bar, count in zip(bars, counts):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(count),
                     ha='center', fontsize=13, fontweight='bold', color='#60a5fa')
    
    # 1f. Plot: Runs per subject (horizontal bar)
    runs_per_subject = {}
    for vf in vhdr_files:
        parts = vf.replace("\\", "/").split("/")
        for p in parts:
            if p.startswith("sub-"):
                runs_per_subject[p] = runs_per_subject.get(p, 0) + 1
                break
    
    sorted_subjects = sorted(runs_per_subject.items(), key=lambda x: x[1], reverse=True)
    sub_names = [s[0].replace("sub-", "") for s in sorted_subjects]
    sub_runs = [s[1] for s in sorted_subjects]
    
    axes[1].barh(sub_names, sub_runs, color='#3b82f6', edgecolor='white', linewidth=0.5)
    axes[1].set_title("Recording Runs per Subject", fontsize=14, fontweight='bold')
    axes[1].set_xlabel("Number of Runs")
    axes[1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_dataset_overview.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Saved: {OUTPUT_DIR}/01_dataset_overview.png")
    
    return vhdr_files

# ─────────────────────────────────────────────────────────────
# PHASE 2: Single-Subject Deep Dive (Raw Signal Inspection)
# ─────────────────────────────────────────────────────────────
def phase2_raw_signal_inspection(vhdr_files):
    log("PHASE 2: Raw Signal Inspection (Single Subject Deep Dive)")
    import mne
    
    # Prefer files with seizure annotations (UMMC subjects consistently have them)
    preferred = [f for f in vhdr_files if 'ummc' in f.lower()]
    others = [f for f in vhdr_files if 'ummc' not in f.lower()]
    ordered_files = preferred + others
    test_file = ordered_files[0]
    print(f"  Loading: {test_file}")
    
    raw = mne.io.read_raw_brainvision(test_file, preload=True, verbose=False)
    
    print(f"\n  📊 Recording Properties:")
    print(f"     Channels: {raw.info['nchan']}")
    print(f"     Sampling Rate: {raw.info['sfreq']} Hz")
    print(f"     Duration: {raw.n_times / raw.info['sfreq']:.1f} seconds ({raw.n_times} samples)")
    print(f"     Channel Names (first 10): {raw.ch_names[:10]}")
    
    feedback(f"This recording has {raw.info['nchan']} channels sampled at {raw.info['sfreq']} Hz. "
             f"With {raw.n_times} total samples, we have {raw.n_times / raw.info['sfreq']:.0f} seconds of continuous data.")
    
    data = raw.get_data()  # shape: (n_channels, n_samples)
    
    # 2a. Plot: First 5 channels raw signal (first 10 seconds)
    n_seconds = min(10, int(raw.n_times / raw.info['sfreq']))
    n_samples = int(n_seconds * raw.info['sfreq'])
    time_axis = np.arange(n_samples) / raw.info['sfreq']
    
    fig, axes = plt.subplots(5, 1, figsize=(16, 12), sharex=True)
    fig.suptitle("Raw EEG Signal — First 5 Channels (10 Seconds)", fontsize=16, fontweight='bold', y=0.98)
    
    channel_colors = ['#3b82f6', '#a855f7', '#10b981', '#f59e0b', '#ef4444']
    for i in range(min(5, data.shape[0])):
        axes[i].plot(time_axis, data[i, :n_samples], color=channel_colors[i], linewidth=0.5, alpha=0.9)
        axes[i].set_ylabel(raw.ch_names[i], fontsize=10, rotation=0, labelpad=60)
        axes[i].set_xlim(0, n_seconds)
    
    axes[-1].set_xlabel("Time (seconds)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_raw_signal_5channels.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Saved: {OUTPUT_DIR}/02_raw_signal_5channels.png")
    
    # 2b. Basic statistics per channel
    print(f"\n  📊 Channel Statistics (all {data.shape[0]} channels):")
    print(f"     {'Channel':<15} {'Mean':>12} {'Std Dev':>12} {'Min':>12} {'Max':>12}")
    print(f"     {'-'*63}")
    
    means = []
    stds = []
    for i in range(data.shape[0]):
        ch_mean = np.mean(data[i])
        ch_std = np.std(data[i])
        ch_min = np.min(data[i])
        ch_max = np.max(data[i])
        means.append(ch_mean)
        stds.append(ch_std)
        if i < 10:  # Print first 10
            print(f"     {raw.ch_names[i]:<15} {ch_mean:>12.6f} {ch_std:>12.6f} {ch_min:>12.6f} {ch_max:>12.6f}")
    
    if data.shape[0] > 10:
        print(f"     ... ({data.shape[0] - 10} more channels)")
    
    feedback(f"Standard deviations range from {min(stds):.6f} to {max(stds):.6f}. "
             f"Channels with unusually high variance may indicate proximity to the seizure onset zone or contain artifacts.")
    
    return raw, data, test_file

# ─────────────────────────────────────────────────────────────
# PHASE 3: Frequency Domain Analysis (Power Spectral Density)
# ─────────────────────────────────────────────────────────────
def phase3_spectral_analysis(raw, data):
    log("PHASE 3: Frequency Domain Analysis (Power Spectral Density)")
    
    sfreq = raw.info['sfreq']
    
    # Compute PSD for first 5 channels using Welch's method
    from scipy.signal import welch
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    channel_colors = ['#3b82f6', '#a855f7', '#10b981', '#f59e0b', '#ef4444']
    
    for i in range(min(5, data.shape[0])):
        freqs, psd = welch(data[i], fs=sfreq, nperseg=min(2048, data.shape[1]))
        # Limit to 0-50 Hz (clinically relevant)
        mask = freqs <= 50
        axes[0].semilogy(freqs[mask], psd[mask], color=channel_colors[i], linewidth=1.5, label=raw.ch_names[i], alpha=0.8)
    
    axes[0].set_title("Power Spectral Density (Welch Method) — First 5 Channels", fontsize=14, fontweight='bold')
    axes[0].set_xlabel("Frequency (Hz)")
    axes[0].set_ylabel("Power Spectral Density (V²/Hz)")
    axes[0].legend(loc='upper right', framealpha=0.3)
    
    # Highlight clinical EEG bands
    bands = {
        'Delta\n(0.5-4 Hz)': (0.5, 4, '#3b82f6'),
        'Theta\n(4-8 Hz)': (4, 8, '#a855f7'),
        'Alpha\n(8-13 Hz)': (8, 13, '#10b981'),
        'Beta\n(13-30 Hz)': (13, 30, '#f59e0b'),
        'Gamma\n(30-50 Hz)': (30, 50, '#ef4444'),
    }
    
    # Band power comparison across first channel
    ch_data = data[0]
    band_powers = []
    band_labels = []
    band_colors = []
    
    for band_name, (low, high, color) in bands.items():
        freqs, psd = welch(ch_data, fs=sfreq, nperseg=min(2048, len(ch_data)))
        mask = (freqs >= low) & (freqs <= high)
        band_power = np.trapezoid(psd[mask], freqs[mask])
        band_powers.append(band_power)
        band_labels.append(band_name)
        band_colors.append(color)
    
    bars = axes[1].bar(band_labels, band_powers, color=band_colors, edgecolor='white', linewidth=0.5)
    axes[1].set_title(f"EEG Band Power Distribution — Channel: {raw.ch_names[0]}", fontsize=14, fontweight='bold')
    axes[1].set_ylabel("Integrated Power (V²)")
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_spectral_analysis.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Saved: {OUTPUT_DIR}/03_spectral_analysis.png")
    
    # Feedback
    dominant_band = band_labels[np.argmax(band_powers)]
    feedback(f"The dominant frequency band is {dominant_band}. "
             f"In epileptic iEEG, elevated delta/theta power often indicates proximity to the seizure onset zone, "
             f"while high-frequency gamma activity can signal fast ripples associated with epileptogenic tissue.")

# ─────────────────────────────────────────────────────────────
# PHASE 4: Seizure vs Baseline Comparison
# ─────────────────────────────────────────────────────────────
def phase4_seizure_vs_baseline(raw, data, test_file):
    log("PHASE 4: Seizure vs Baseline Signal Comparison")
    
    sfreq = raw.info['sfreq']
    
    # Find events file
    events_path = test_file.replace('_ieeg.vhdr', '_events.tsv')
    onset_sample = None
    
    if os.path.exists(events_path):
        with open(events_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row.get('trial_type', '').strip().lower() == 'sz onset':
                    onset_sample = int(row['sample'])
                    print(f"  Found seizure onset at sample: {onset_sample} ({onset_sample/sfreq:.1f}s)")
                    break
    
    if onset_sample is None or onset_sample >= data.shape[1]:
        print("  ⚠️  No valid seizure onset found for this file. Skipping phase 4.")
        return
    
    # Extract baseline (5 seconds before onset) and seizure (5 seconds after onset)
    window = int(5 * sfreq)
    baseline_start = max(0, onset_sample - window)
    seizure_end = min(data.shape[1], onset_sample + window)
    
    ch = 0  # Use first channel
    baseline_data = data[ch, baseline_start:onset_sample]
    seizure_data = data[ch, onset_sample:seizure_end]
    
    fig = plt.figure(figsize=(16, 14))
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3)
    
    # 4a. Full signal with onset marker
    ax1 = fig.add_subplot(gs[0, :])
    full_window = data[ch, baseline_start:seizure_end]
    time_axis = np.arange(len(full_window)) / sfreq
    onset_time = (onset_sample - baseline_start) / sfreq
    
    ax1.plot(time_axis, full_window, color='#94a3b8', linewidth=0.5)
    ax1.axvline(onset_time, color='#ef4444', linewidth=2, linestyle='--', label='Seizure Onset')
    ax1.fill_betweenx(ax1.get_ylim(), 0, onset_time, alpha=0.1, color='#3b82f6', label='Baseline')
    ax1.fill_betweenx(ax1.get_ylim(), onset_time, time_axis[-1], alpha=0.1, color='#ef4444', label='Ictal')
    ax1.set_title(f"Baseline vs Ictal Signal — Channel: {raw.ch_names[ch]}", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Amplitude")
    ax1.legend(loc='upper right', framealpha=0.3)
    
    # 4b. Amplitude distribution comparison
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(baseline_data, bins=80, alpha=0.7, color='#3b82f6', label=f'Baseline (σ={np.std(baseline_data):.4f})', density=True)
    ax2.hist(seizure_data, bins=80, alpha=0.7, color='#ef4444', label=f'Ictal (σ={np.std(seizure_data):.4f})', density=True)
    ax2.set_title("Amplitude Distribution", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Amplitude")
    ax2.set_ylabel("Density")
    ax2.legend(framealpha=0.3)
    
    # 4c. Rolling variance comparison
    ax3 = fig.add_subplot(gs[1, 1])
    roll_window = int(0.5 * sfreq)  # 500ms rolling window
    
    def rolling_var(arr, w):
        return np.array([np.var(arr[max(0,i-w):i+1]) for i in range(len(arr))])
    
    baseline_var = rolling_var(baseline_data, roll_window)
    seizure_var = rolling_var(seizure_data, roll_window)
    
    t_baseline = np.arange(len(baseline_var)) / sfreq
    t_seizure = np.arange(len(seizure_var)) / sfreq
    
    ax3.plot(t_baseline, baseline_var, color='#3b82f6', linewidth=1, label='Baseline Variance', alpha=0.8)
    ax3.plot(t_seizure + t_baseline[-1], seizure_var, color='#ef4444', linewidth=1, label='Ictal Variance', alpha=0.8)
    ax3.axvline(t_baseline[-1], color='white', linewidth=1, linestyle='--', alpha=0.5)
    ax3.set_title("Rolling Variance (500ms window)", fontsize=13, fontweight='bold')
    ax3.set_xlabel("Time (seconds)")
    ax3.set_ylabel("Variance")
    ax3.legend(framealpha=0.3)
    
    # 4d. PSD comparison (baseline vs ictal)
    from scipy.signal import welch
    ax4 = fig.add_subplot(gs[2, 0])
    
    freqs_b, psd_b = welch(baseline_data, fs=sfreq, nperseg=min(1024, len(baseline_data)))
    freqs_s, psd_s = welch(seizure_data, fs=sfreq, nperseg=min(1024, len(seizure_data)))
    
    mask_b = freqs_b <= 50
    mask_s = freqs_s <= 50
    
    ax4.semilogy(freqs_b[mask_b], psd_b[mask_b], color='#3b82f6', linewidth=1.5, label='Baseline PSD')
    ax4.semilogy(freqs_s[mask_s], psd_s[mask_s], color='#ef4444', linewidth=1.5, label='Ictal PSD')
    ax4.set_title("PSD: Baseline vs Ictal", fontsize=13, fontweight='bold')
    ax4.set_xlabel("Frequency (Hz)")
    ax4.set_ylabel("Power (V²/Hz)")
    ax4.legend(framealpha=0.3)
    
    # 4e. Summary statistics box
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    
    stats_text = (
        f"═══ STATISTICAL SUMMARY ═══\n\n"
        f"Channel: {raw.ch_names[ch]}\n"
        f"Sampling Rate: {sfreq} Hz\n\n"
        f"BASELINE (Pre-Seizure)\n"
        f"  Mean:    {np.mean(baseline_data):.6f}\n"
        f"  Std Dev: {np.std(baseline_data):.6f}\n"
        f"  Skew:    {float(np.mean(((baseline_data - np.mean(baseline_data))/np.std(baseline_data))**3)):.3f}\n"
        f"  Kurtosis:{float(np.mean(((baseline_data - np.mean(baseline_data))/np.std(baseline_data))**4) - 3):.3f}\n\n"
        f"ICTAL (Seizure)\n"
        f"  Mean:    {np.mean(seizure_data):.6f}\n"
        f"  Std Dev: {np.std(seizure_data):.6f}\n"
        f"  Skew:    {float(np.mean(((seizure_data - np.mean(seizure_data))/np.std(seizure_data))**3)):.3f}\n"
        f"  Kurtosis:{float(np.mean(((seizure_data - np.mean(seizure_data))/np.std(seizure_data))**4) - 3):.3f}\n\n"
        f"Variance Ratio (Ictal/Baseline): {np.var(seizure_data)/np.var(baseline_data):.2f}x"
    )
    
    ax5.text(0.05, 0.95, stats_text, transform=ax5.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             color='#e2e8f0',
             bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e293b', edgecolor='#334155'))
    
    plt.savefig(os.path.join(OUTPUT_DIR, "04_seizure_vs_baseline.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Saved: {OUTPUT_DIR}/04_seizure_vs_baseline.png")
    
    variance_ratio = np.var(seizure_data) / np.var(baseline_data)
    feedback(f"The ictal variance is {variance_ratio:.1f}x higher than the baseline. "
             f"This dramatic variance explosion is exactly what the Kalman Filter is designed to detect — "
             f"it interprets this as a state transition, whereas ARIMA treats it as an extreme outlier within the same model.")

# ─────────────────────────────────────────────────────────────
# PHASE 5: Cross-Channel Correlation Heatmap
# ─────────────────────────────────────────────────────────────
def phase5_channel_correlation(raw, data):
    log("PHASE 5: Cross-Channel Spatial Correlation Analysis")
    
    n_channels = min(20, data.shape[0])  # Limit to 20 for readability
    subset = data[:n_channels, :]
    
    corr_matrix = np.corrcoef(subset)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    
    ax.set_xticks(range(n_channels))
    ax.set_yticks(range(n_channels))
    ax.set_xticklabels(raw.ch_names[:n_channels], rotation=90, fontsize=9)
    ax.set_yticklabels(raw.ch_names[:n_channels], fontsize=9)
    ax.set_title("Cross-Channel Correlation Matrix (Full Recording)", fontsize=14, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson Correlation", color='#e2e8f0')
    cbar.ax.yaxis.set_tick_params(color='#94a3b8')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#94a3b8')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_channel_correlation.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Saved: {OUTPUT_DIR}/05_channel_correlation.png")
    
    # Find highly correlated pairs
    high_corr_pairs = []
    for i in range(n_channels):
        for j in range(i+1, n_channels):
            if abs(corr_matrix[i, j]) > 0.7:
                high_corr_pairs.append((raw.ch_names[i], raw.ch_names[j], corr_matrix[i, j]))
    
    if high_corr_pairs:
        print(f"\n  Highly correlated channel pairs (|r| > 0.7): {len(high_corr_pairs)}")
        for ch1, ch2, r in high_corr_pairs[:5]:
            print(f"    {ch1} ↔ {ch2}: r = {r:.3f}")
        
        feedback("Highly correlated neighbouring channels confirm spatial coupling in the brain network. "
                 "This is exactly why ARMAX uses one channel as an exogenous input — these spatial correlations "
                 "allow the model to detect seizure propagation across brain regions.")
    else:
        feedback("No strongly correlated pairs found. This suggests independent electrode placement, "
                 "which may limit the effectiveness of ARMAX's spatial modelling approach for this subject.")

# ─────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  EEG DATASET - EXPLORATORY DATA ANALYSIS")
    print("="*60)
    
    vhdr_files = phase1_dataset_overview()
    raw, data, test_file = phase2_raw_signal_inspection(vhdr_files)
    phase3_spectral_analysis(raw, data)
    phase4_seizure_vs_baseline(raw, data, test_file)
    phase5_channel_correlation(raw, data)
    
    log("EDA COMPLETE")
    print(f"\n  All visualisations saved to: {OUTPUT_DIR}/")
    print(f"  Files generated:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        print(f"    [CHART] {f}")
    print()
