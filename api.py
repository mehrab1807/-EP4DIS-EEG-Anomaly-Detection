import os
import time
import glob
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from preprocess import preprocess_eeg
from models.arima_detector import ARIMADetector
from models.armax_detector import ARMAXDetector
from models.kalman_detector import KalmanDetector

app = FastAPI(title="EEG Anomaly Detection API")

# Add CORS so our React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory for the vanilla frontend
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

class AnalyzeRequest(BaseModel):
    file_path: str

@app.get("/api/patients")
def get_patients():
    """Scans the data directory and returns available EEG runs."""
    base_dir = os.path.abspath("data")
    if not os.path.exists(base_dir):
        return {"patients": []}
    
    vhdr_files = []
    for root, dirs, files in os.walk(base_dir, followlinks=True):
        for file in files:
            if file.endswith(".vhdr"):
                vhdr_files.append(os.path.join(root, file))
    
    patients = []
    for file_path in vhdr_files:
        # Normalize path separators for the frontend
        # We need a path relative to the root for the file_path arg, or absolute
        normalized_path = file_path.replace("\\", "/")
        filename = os.path.basename(normalized_path)
        
        parts = filename.split('_')
        sub = next((p for p in parts if p.startswith('sub-')), 'Unknown')
        run = next((p for p in parts if p.startswith('run-')), 'Unknown')
        
        display_name = f"{sub.upper()} - {run.upper()}"
        
        patients.append({
            "id": normalized_path,
            "display_name": display_name
        })
    
    patients.sort(key=lambda x: x["display_name"])
    return {"patients": patients}

@app.post("/api/analyze")
def analyze_eeg(request: AnalyzeRequest):
    """Runs the full pipeline on a selected EEG file."""
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="EEG file not found.")
        
    try:
        # Preprocess
        primary_eeg_channel, secondary_eeg_channel, seizure_start_index = preprocess_eeg(request.file_path)
        
        baseline_length = min(2000, seizure_start_index) 
        baseline_eeg_primary = primary_eeg_channel[:baseline_length]
        seizure_eeg_primary = primary_eeg_channel[baseline_length:]
        
        baseline_eeg_secondary = secondary_eeg_channel[:baseline_length]
        seizure_eeg_secondary = secondary_eeg_channel[baseline_length:]
        
        # --- ARIMA ---
        start = time.time()
        arima = ARIMADetector(order=(3, 0, 0), threshold_std=3.0)
        arima.fit(baseline_eeg_primary)
        arima_seizure_flags, _ = arima.detect(seizure_eeg_primary)
        arima_time = time.time() - start
        
        # --- ARMAX ---
        start = time.time()
        armax = ARMAXDetector(order=(3, 0, 0), threshold_std=3.0)
        armax.fit(baseline_eeg_primary, baseline_eeg_secondary)
        armax_seizure_flags, _ = armax.detect(seizure_eeg_primary, seizure_eeg_secondary)
        armax_time = time.time() - start
        
        # --- Kalman Filter ---
        start = time.time()
        kf = KalmanDetector(threshold_std=3.0)
        kf.fit(baseline_eeg_primary)
        kalman_seizure_flags, _, _ = kf.detect(seizure_eeg_primary)
        kf_time = time.time() - start
        
        # Format for frontend response
        # Reconstruct the full arrays (baseline + test) so the frontend can plot it sequentially
        full_signal = primary_eeg_channel.tolist()
        
        def pad_anomalies(flags):
            import numpy as np
            # Prepend False for the baseline length
            return np.concatenate([np.zeros(baseline_length, dtype=bool), flags]).tolist()
            
        return {
            "signal": full_signal,
            "seizure_start_index": int(seizure_start_index),
            "arima": {
                "time": round(arima_time, 3),
                "anomalies_detected": int(arima_seizure_flags.sum()),
                "flags": pad_anomalies(arima_seizure_flags)
            },
            "armax": {
                "time": round(armax_time, 3),
                "anomalies_detected": int(armax_seizure_flags.sum()),
                "flags": pad_anomalies(armax_seizure_flags)
            },
            "kalman": {
                "time": round(kf_time, 3),
                "anomalies_detected": int(kalman_seizure_flags.sum()),
                "flags": pad_anomalies(kalman_seizure_flags)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
