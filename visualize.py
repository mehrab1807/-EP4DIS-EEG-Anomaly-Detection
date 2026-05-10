import numpy as np
import matplotlib.pyplot as plt

def plot_results():
    data = np.load("results.npz")
    baseline_eeg_primary = data['baseline_eeg_primary']
    seizure_eeg_primary = data['seizure_eeg_primary']
    
    full_target = np.concatenate([baseline_eeg_primary, seizure_eeg_primary])
    
    # Reconstruct anomaly vectors to match full length
    def pad_anomalies(anoms):
        return np.concatenate([np.zeros(len(baseline_eeg_primary), dtype=bool), anoms])
        
    arima_anom = pad_anomalies(data['arima_seizure_flags'])
    armax_anom = pad_anomalies(data['armax_seizure_flags'])
    kf_anom = pad_anomalies(data['kalman_seizure_flags'])
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    # 1. Raw Data
    axes[0].plot(full_target, label="EEG Signal", color="black", alpha=0.7)
    axes[0].axvline(len(baseline_eeg_primary), color='red', linestyle='--', label="Seizure Onset")
    axes[0].set_title("Raw Clinical EEG Signal")
    axes[0].legend()
    
    # 2. ARIMA
    axes[1].plot(full_target, color="black", alpha=0.3)
    axes[1].plot(np.where(arima_anom)[0], full_target[arima_anom], 'ro', label="ARIMA Anomaly", markersize=3)
    axes[1].set_title("ARIMA Detection")
    axes[1].legend()
    
    # 3. ARMAX
    axes[2].plot(full_target, color="black", alpha=0.3)
    axes[2].plot(np.where(armax_anom)[0], full_target[armax_anom], 'bo', label="ARMAX Anomaly", markersize=3)
    axes[2].set_title("ARMAX Detection (with spatial exog. variable)")
    axes[2].legend()
    
    # 4. Kalman
    axes[3].plot(full_target, color="black", alpha=0.3)
    axes[3].plot(np.where(kf_anom)[0], full_target[kf_anom], 'go', label="Kalman Filter Anomaly", markersize=3)
    axes[3].set_title("Kalman Filter Detection")
    axes[3].legend()
    
    plt.tight_layout()
    plt.savefig("detection_comparison.png")
    print("Plot saved as detection_comparison.png")

if __name__ == "__main__":
    plot_results()
