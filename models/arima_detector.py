import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

class ARIMADetector:
    def __init__(self, order=(5, 1, 0), threshold_std=3.0):
        self.order = order
        self.threshold_std = threshold_std
        self.model_fit = None
        self.residuals = None
        self.threshold = 0
        
    def fit(self, baseline_eeg):
        """Fit ARIMA model on a baseline/healthy segment of data."""
        model = ARIMA(baseline_eeg, order=self.order)
        self.model_fit = model.fit()
        self.residuals = self.model_fit.resid
        self.threshold = np.mean(self.residuals) + self.threshold_std * np.std(self.residuals)
        
    def detect(self, seizure_eeg):
        """Detect anomalies in new data."""
        model = ARIMA(seizure_eeg, order=self.order)
        res = model.filter(self.model_fit.params)
        test_residuals = res.resid
        
        anomalies = np.abs(test_residuals) > self.threshold
        return anomalies, test_residuals
