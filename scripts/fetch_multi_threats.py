# scripts/fetch_multi_threats.py
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json
import time

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
OTX_API_KEY = os.getenv("OTX_API_KEY")  # AlienVault OTX key


# ---------------------- AbuseIPDB ----------------------
def call_abuseipdb(ip, max_age_days=90):
    """Fetch IP reputation from AbuseIPDB"""
    if not ABUSEIPDB_API_KEY:
        return {"error": "No AbuseIPDB API key configured"}
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": str(max_age_days)}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get("data", {})
        else:
            return {"error": f"AbuseIPDB status {r.status_code}", "raw": r.text}
    except requests.RequestException as e:
        return {"error": f"AbuseIPDB request failed: {e}"}


# ---------------------- AlienVault OTX ----------------------
def call_otx(ip):
    """Fetch IP reputation from AlienVault OTX"""
    if not OTX_API_KEY:
        return {"error": "No OTX API key configured"}
    url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"OTX status {r.status_code}", "raw": r.text}
    except requests.RequestException as e:
        return {"error": f"OTX request failed: {e}"}


# ---------------------- Enrichment ----------------------
def enrich_ip(ip, include_abuse=True, include_otx=True, pause_between=1.5):
    """
    Enrich a single IP using AbuseIPDB and AlienVault OTX.
    """
    result = {"ip": ip, "fetched_at": datetime.utcnow().isoformat(), "sources": {}}

    if include_abuse:
        result["sources"]["abuseipdb"] = call_abuseipdb(ip)
        time.sleep(pause_between)

    if include_otx:
        result["sources"]["otx"] = call_otx(ip)
        time.sleep(pause_between)

    return result


# ---------------------- Main Runner ----------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch_multi_threats.py <ip>")
        sys.exit(1)

    ip = sys.argv[1]
    combined = enrich_ip(ip)

    out_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / f"enriched_{ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print(f"✅ Saved enrichment to {out_path}")
