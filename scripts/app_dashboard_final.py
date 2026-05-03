import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import json
import os
from datetime import datetime

# -------------------------------------------------------------
# 🌐 Page Setup
# -------------------------------------------------------------
st.set_page_config(
    page_title="Cyber Threat Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <h1 style='text-align:center; color:#00adb5;'>🛡️ Cyber Threat Intelligence Dashboard</h1>
    <p style='text-align:center; color:gray;'>Live IP Intelligence powered by AbuseIPDB & AlienVault OTX</p>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 🎯 IP Input Section
# -------------------------------------------------------------
st.sidebar.header("🔍 IP Lookup")
ip_to_check = st.sidebar.text_input("Enter IP Address", placeholder="e.g. 8.8.8.8")

if ip_to_check:
    st.sidebar.info("Fetching data... Please wait ⏳")

    # Run fetch_multi_threats.py to get data for the entered IP
    result_path = os.path.join("data", f"enriched_{ip_to_check}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    try:
        subprocess.run(["python", "scripts/fetch_multi_threats.py", ip_to_check], check=True)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

    # Load the newest enriched file
    enriched_files = [f for f in os.listdir("data") if f.startswith(f"enriched_{ip_to_check}_") and f.endswith(".json")]
    latest_file = max(enriched_files, key=lambda x: os.path.getctime(os.path.join("data", x)))
    file_path = os.path.join("data", latest_file)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.success(f"✅ Data fetched for **{ip_to_check}**")
else:
    st.info("Enter an IP address in the sidebar to start analysis.")
    st.stop()

# -------------------------------------------------------------
# 🧩 Data Extraction
# -------------------------------------------------------------
abuse_data = data.get("sources", {}).get("abuseipdb", {})
otx_data = data.get("sources", {}).get("otx", {})
fetched_at = data.get("fetched_at", "N/A")

# -------------------------------------------------------------
# 🧠 Display Summary Info
# -------------------------------------------------------------
st.markdown("### 🌍 Enrichment Summary")
col1, col2 = st.columns(2)
col1.metric("🔹 IP Address", ip_to_check)
col2.metric("📅 Data Fetched At", fetched_at)

# -------------------------------------------------------------
# 📊 AbuseIPDB Summary
# -------------------------------------------------------------
if abuse_data:
    st.markdown("### 🚨 AbuseIPDB Analysis")
    colA1, colA2, colA3 = st.columns(3)

    abuse_score = abuse_data.get("abuseConfidenceScore", 0)
    total_reports = abuse_data.get("totalReports", 0)
    country = abuse_data.get("countryCode", "Unknown")

    colA1.metric("Confidence Score", abuse_score)
    colA2.metric("Total Reports", total_reports)
    colA3.metric("Country", country)

    st.markdown("#### 🧾 Details")
    clean_abuse = {k: v for k, v in abuse_data.items() if v not in [None, "", [], {}]}
    st.json(clean_abuse)
else:
    st.warning("No AbuseIPDB data available for this IP.")

# -------------------------------------------------------------
# 👽 AlienVault OTX Summary
# -------------------------------------------------------------
if otx_data:
    st.markdown("### 👽 AlienVault OTX Analysis")

    reputation = otx_data.get("reputation", "N/A")
    indicator = otx_data.get("indicator", "N/A")
    pulse_info = otx_data.get("pulse_info", {}).get("count", 0)

    colO1, colO2, colO3 = st.columns(3)
    colO1.metric("Reputation", reputation)
    colO2.metric("Pulses", pulse_info)
    colO3.metric("Indicator Type", otx_data.get("type", "N/A"))

    st.markdown("#### 🧾 Details")
    clean_otx = {k: v for k, v in otx_data.items() if v not in [None, "", [], {}]}
    st.json(clean_otx)
else:
    st.warning("No OTX data available for this IP.")

# -------------------------------------------------------------
# 📈 Visual Analytics
# -------------------------------------------------------------
st.markdown("### 📈 Visual Insights")

metrics = {
    "Abuse Confidence": abuse_data.get("abuseConfidenceScore", 0),
    "OTX Reputation": otx_data.get("reputation", 0),
    "OTX Pulse Count": otx_data.get("pulse_info", {}).get("count", 0),
    "Total Reports": abuse_data.get("totalReports", 0),
}

df_chart = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
fig = px.bar(df_chart, x="Metric", y="Value", color="Metric", text_auto=True,
             title=f"Threat Metrics Overview for {ip_to_check}",
             color_discrete_sequence=px.colors.qualitative.Set2)
fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# ✅ Footer
# -------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Cyber Threat Dashboard © 2025 | Powered by AbuseIPDB & AlienVault OTX</p>",
    unsafe_allow_html=True
)
