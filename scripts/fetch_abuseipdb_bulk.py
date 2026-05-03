import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

print("🚀 Starting bulk data collection...")

# Load API key from the .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("ABUSEIPDB_API_KEY")

if not API_KEY:
    print("❌ ERROR: API key not found. Check your .env file.")
    exit()

# Prepare headers
headers = {
    "Key": API_KEY,
    "Accept": "application/json"
}

# API endpoint
url = "https://api.abuseipdb.com/api/v2/blacklist"


# Folder to save data
data_folder = Path(__file__).resolve().parent.parent / "data"
data_folder.mkdir(parents=True, exist_ok=True)

# File name with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = data_folder / f"abuseipdb_reports_{timestamp}.json"

# Fetch several pages
all_reports = []
print("🌍 Fetching blacklist data ...")
params = {
    "confidenceMinimum": "50",  # only keep IPs with confidence >= 50
    "limit": "10000"            # max 10,000 records
}

response = requests.get(url, headers=headers, params=params)
print("   Status code:", response.status_code)

if response.status_code != 200:
    print("❌ Request failed:", response.text)
    exit()

data = response.json()
reports = data.get("data", [])
all_reports.extend(reports)


# Save all data
with open(output_file, "w") as f:
    json.dump(all_reports, f, indent=4)

print(f"✅ Saved {len(all_reports)} reports to {output_file}")
