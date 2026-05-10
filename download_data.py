import openneuro
import os

DATASET = "ds003029"
TARGET_DIR = "data"

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

print(f"Downloading full dataset {DATASET} to {TARGET_DIR} (approx. 11.08 GB)...")
openneuro.download(dataset=DATASET, target_dir=TARGET_DIR)
print("Download complete.")
