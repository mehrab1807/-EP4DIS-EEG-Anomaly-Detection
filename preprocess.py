import numpy as np
import os

def preprocess_eeg(file_path=None):
    """Loads and preprocesses real EEG data."""
    if file_path and os.path.exists(file_path):
        import mne
        import csv
        
        # Load raw data
        raw = mne.io.read_raw_brainvision(file_path, preload=True)
        raw.filter(l_freq=1.0, h_freq=40.0) # Bandpass filter
        
        # Find the events file to get seizure onset
        events_path = file_path.replace('_ieeg.vhdr', '_events.tsv')
        onset_sample = 2000 # default fallback
        if os.path.exists(events_path):
            with open(events_path, 'r') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    if row['trial_type'] == 'sz onset':
                        onset_sample = int(row['sample'])
                        print(f"Found seizure onset at sample: {onset_sample}")
                        break
                        
        # Check if onset_sample is out of bounds
        if onset_sample >= raw.n_times:
            raise ValueError(f"Error: Seizure onset ({onset_sample}) exceeds data length ({raw.n_times}). The EEG file is likely incomplete or truncated.")
        
        # Extract a window around the seizure (e.g., 2000 before, 2000 after)
        window_start = max(0, onset_sample - 2000)
        window_end = min(raw.n_times, onset_sample + 2000)
        
        data, times = raw[:, window_start:window_end]
        
        # Return first two channels as target and exog, and the relative anomaly index
        primary_eeg_channel = data[0, :]
        secondary_eeg_channel = data[1, :]
        seizure_start_index = onset_sample - window_start
        
        return primary_eeg_channel, secondary_eeg_channel, seizure_start_index
    else:
        raise FileNotFoundError(f"EEG file not found: {file_path}")
