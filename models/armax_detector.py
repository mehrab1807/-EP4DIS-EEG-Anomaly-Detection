import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

class ARMAXDetector:
    def __init__(self, order=(5, 1, 0), threshold_std=3.0):
        self.order = order
        self.threshold_std = threshold_std
        self.model_fit = None
        self.residuals = None
        self.threshold = 0
        
    def fit(self, baseline_eeg, secondary_eeg_baseline):
        """Fit ARMAX model using external spatial variables (secondary_eeg_baseline)."""
        model = ARIMA(baseline_eeg, exog=secondary_eeg_baseline, order=self.order)
        self.model_fit = model.fit()
        self.residuals = self.model_fit.resid
        self.threshold = np.mean(self.residuals) + self.threshold_std * np.std(self.residuals)
        
    def detect(self, seizure_eeg, secondary_eeg_seizure):
        """Detect anomalies incorporating exogenous data."""
        model = ARIMA(seizure_eeg, exog=secondary_eeg_seizure, order=self.order)
        res = model.filter(self.model_fit.params)
        test_residuals = res.resid
        anomalies = np.abs(test_residuals) > self.threshold
        return anomalies, test_residuals
