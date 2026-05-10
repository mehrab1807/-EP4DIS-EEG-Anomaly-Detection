import os
import time
from preprocess import preprocess_eeg
from models.arima_detector import ARIMADetector
from models.armax_detector import ARMAXDetector
from models.kalman_detector import KalmanDetector

def main():
    print("Loading data...")
    # Attempt to use downloaded OpenNeuro data if it exists
    dataset_path = "data/sub-ummc008/ses-presurgery/ieeg/sub-ummc008_ses-presurgery_task-ictal_acq-ecog_run-01_ieeg.vhdr"
    primary_eeg_channel, secondary_eeg_channel, seizure_start_index = preprocess_eeg(dataset_path)
    
    print(f"Data shape: {primary_eeg_channel.shape}, True Onset Index in window: {seizure_start_index}")
    
    # Split into train (baseline) and test (contains anomaly)
    # Use 2000 samples before the true onset as training data
    baseline_length = min(2000, seizure_start_index) 
    baseline_eeg_primary, seizure_eeg_primary = primary_eeg_channel[:baseline_length], primary_eeg_channel[baseline_length:]
    baseline_eeg_secondary, seizure_eeg_secondary = secondary_eeg_channel[:baseline_length], secondary_eeg_channel[baseline_length:]
    
    # --- ARIMA ---
    print("\n--- Running ARIMA ---")
    start = time.time()
    arima = ARIMADetector(order=(3, 0, 0), threshold_std=3.0)
    arima.fit(baseline_eeg_primary)
    arima_seizure_flags, arima_prediction_errors = arima.detect(seizure_eeg_primary)
    print(f"ARIMA Time: {time.time() - start:.3f}s")
    print(f"ARIMA Anomalies Detected: {arima_seizure_flags.sum()}")
    
    # --- ARMAX ---
    print("\n--- Running ARMAX ---")
    start = time.time()
    armax = ARMAXDetector(order=(3, 0, 0), threshold_std=3.0)
    armax.fit(baseline_eeg_primary, baseline_eeg_secondary)
    armax_seizure_flags, armax_prediction_errors = armax.detect(seizure_eeg_primary, seizure_eeg_secondary)
    print(f"ARMAX Time: {time.time() - start:.3f}s")
    print(f"ARMAX Anomalies Detected: {armax_seizure_flags.sum()}")
    
    # --- Kalman Filter ---
    print("\n--- Running Kalman Filter ---")
    start = time.time()
    kf = KalmanDetector(threshold_std=3.0)
    kf.fit(baseline_eeg_primary)
    kalman_seizure_flags, kalman_prediction_errors, _ = kf.detect(seizure_eeg_primary)
    print(f"Kalman Filter Time: {time.time() - start:.3f}s")
    print(f"Kalman Anomalies Detected: {kalman_seizure_flags.sum()}")
    
    # Save results for visualization
    import numpy as np
    np.savez("results.npz", 
             baseline_eeg_primary=baseline_eeg_primary, seizure_eeg_primary=seizure_eeg_primary,
             arima_seizure_flags=arima_seizure_flags, arima_prediction_errors=arima_prediction_errors,
             armax_seizure_flags=armax_seizure_flags, armax_prediction_errors=armax_prediction_errors,
             kalman_seizure_flags=kalman_seizure_flags, kalman_prediction_errors=kalman_prediction_errors)
    print("\nResults saved to results.npz. Run visualize.py to view plots.")

if __name__ == "__main__":
    main()
