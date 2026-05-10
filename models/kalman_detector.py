import numpy as np
from pykalman import KalmanFilter

class KalmanDetector:
    def __init__(self, threshold_std=3.0):
        self.threshold_std = threshold_std
        self.kf = None
        self.baseline_mean = 0
        self.baseline_std = 1
        self.threshold = 0
        
    def fit(self, baseline_eeg):
        """Fit the Kalman Filter to baseline data to learn system parameters using EM."""
        # Simple 1D state space model
        self.kf = KalmanFilter(transition_matrices=[1],
                               observation_matrices=[1],
                               initial_state_mean=baseline_eeg[0],
                               initial_state_covariance=1,
                               observation_covariance=1,
                               transition_covariance=0.01)
        
        self.kf = self.kf.em(baseline_eeg, n_iter=5)
        
        # Calculate baseline innovations
        state_means, _ = self.kf.filter(baseline_eeg)
        innovations = baseline_eeg - state_means.flatten()
        self.baseline_mean = np.mean(innovations)
        self.baseline_std = np.std(innovations)
        self.threshold = self.baseline_mean + self.threshold_std * self.baseline_std
        
    def detect(self, seizure_eeg):
        """Track state and detect anomalies based on innovation sequence."""
        state_means, _ = self.kf.filter(seizure_eeg)
        innovations = seizure_eeg - state_means.flatten()
        anomalies = np.abs(innovations) > self.threshold
        return anomalies, innovations, state_means.flatten()
