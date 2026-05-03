import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
print("📁 Current working directory:", os.getcwd())

print("🚀 Starting script...")

# Load API key from .env file
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
print("🔍 Loaded .env from:", env_path)

API_KEY = os.getenv("ABUSEIPDB_API_KEY")
print("🔑 API Key loaded:", API_KEY)

if not API_KEY:
    print("❌ ERROR: API key not found! Make sure .env file exists in the main project folder.")
    exit()

# API endpoint and request setup
url = "https://api.abuseipdb.com/api/v2/check"
params = {"ipAddress": "1.1.1.1", "maxAgeInDays": "90"}
headers = {"Key": API_KEY, "Accept": "application/json"}

print("🌍 Sending request to AbuseIPDB...")
response = requests.get(url, headers=headers, params=params)
print("🔁 Status Code:", response.status_code)

if response.status_code != 200:
    print("❌ Request failed. Response:")
    print(response.text)
    exit()

# Save JSON output
data = response.json()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(Path(__file__).resolve().parent.parent, "data", f"abuseipdb_{timestamp}.json")


with open(filename, "w") as f:
    json.dump(data, f, indent=4)

print(f"✅ Data saved to {filename}")

