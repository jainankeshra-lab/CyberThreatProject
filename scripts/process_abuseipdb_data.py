import json
import pandas as pd
from pathlib import Path

print("🚀 Starting data preprocessing...")

# Path to your data folder and file
data_folder = Path(__file__).resolve().parent.parent / "data"
latest_file = max(data_folder.glob("abuseipdb_reports_*.json"), key=lambda f: f.stat().st_mtime)
print("📂 Using latest file:", latest_file)

# Load JSON data
with open(latest_file, "r") as f:
    data = json.load(f)

print(f"✅ Loaded {len(data)} records")

# Convert to DataFrame
df = pd.json_normalize(data)
print("🧱 Columns found:", df.columns.tolist()[:10], "...")

# Basic cleaning
df.drop_duplicates(subset=["ipAddress"], inplace=True)
df.reset_index(drop=True, inplace=True)

# Save to CSV
csv_path = data_folder / (latest_file.stem + ".csv")
df.to_csv(csv_path, index=False)

print(f"✅ Clean CSV saved to {csv_path}")
print("🧠 Sample rows:")
print(df.head())
