import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("🚀 Starting data analysis...")

# Locate the latest CSV file in the data folder
data_folder = Path(__file__).resolve().parent.parent / "data"
latest_csv = max(data_folder.glob("abuseipdb_reports_*.csv"), key=lambda f: f.stat().st_mtime)
print("📂 Using latest file:", latest_csv)

# Load the CSV file
df = pd.read_csv(latest_csv)
print(f"✅ Loaded {len(df)} records")

# Show first few rows
print("🧠 Sample data:")
print(df.head())

# --- Basic Statistics ---
print("\n📊 Basic Statistics:")
print("Total unique IPs:", df['ipAddress'].nunique())
print("Average confidence score:", df['abuseConfidenceScore'].mean())
print("Top 5 countries by number of malicious IPs:")
print(df['countryCode'].value_counts().head(5))

# --- Visualization 1: Top 10 Countries ---
top_countries = df['countryCode'].value_counts().head(10)
plt.figure(figsize=(10, 5))
top_countries.plot(kind='bar', color='orange')
plt.title("🌍 Top 10 Countries by Reported Malicious IPs")
plt.xlabel("Country Code")
plt.ylabel("Number of IPs")
plt.tight_layout()
plt.show()

# --- Visualization 2: Distribution of Confidence Scores ---
plt.figure(figsize=(8, 4))
df['abuseConfidenceScore'].hist(bins=20, color='steelblue', edgecolor='black')
plt.title("🎯 Distribution of Abuse Confidence Scores")
plt.xlabel("Confidence Score")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()
