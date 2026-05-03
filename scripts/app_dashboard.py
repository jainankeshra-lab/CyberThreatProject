# scripts/app_dashboard_v2.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fetch_multi_threats import enrich_ip  # <-- using your existing script

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Cyber Threat Intelligence Portal",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <h1 style='text-align:center; color:#00adb5;'>🛡️ Cyber Threat Intelligence Portal</h1>
    <p style='text-align:center; color:gray;'>Live IP Threat Analysis using AbuseIPDB, AlienVault OTX & ThreatCrowd</p>
    """,
    unsafe_allow_html=True
)

# ------------------- USER INPUT -------------------
ip_input = st.text_input("🔍 Enter an IP address to analyze:", placeholder="e.g., 8.8.8.8")
analyze_button = st.button("Analyze IP")

# ------------------- MAIN LOGIC -------------------
if analyze_button and ip_input.strip():
    with st.spinner(f"Fetching threat intelligence for {ip_input} ..."):
        result = enrich_ip(ip_input.strip())

    if "error" in result.get("sources", {}).get("abuseipdb", {}):
        st.error(f"⚠️ {result['sources']['abuseipdb']['error']}")
    else:
        st.success("✅ Data fetched successfully!")

    # ------------------- BASIC DETAILS -------------------
    st.markdown("### 🌍 Enrichment Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("IP Address", result.get("ip"))
    with col2:
        st.metric("Fetched At", result.get("fetched_at", "N/A"))

    sources = result.get("sources", {})
    abuse_data = sources.get("abuseipdb", {})
    otx_data = sources.get("otx", {})
    tc_data = sources.get("threatcrowd", {})

    # ------------------- SOURCE-WISE DATA -------------------
    st.markdown("### 🧩 Source Intelligence Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("AbuseIPDB")
        st.json(abuse_data)
    with col2:
        st.subheader("AlienVault OTX")
        st.json(otx_data)
    with col3:
        st.subheader("ThreatCrowd")
        st.json(tc_data)

    # ------------------- VISUALIZATION -------------------
    st.markdown("---")
    st.markdown("### 📊 Threat Analytics Overview")

    abuse_score = abuse_data.get("abuseConfidenceScore", None)
    country = abuse_data.get("countryCode", "Unknown")

    # Convert values safely
    if isinstance(abuse_score, str) and abuse_score.isdigit():
        abuse_score = int(abuse_score)
    elif isinstance(abuse_score, (float, int)):
        abuse_score = int(abuse_score)
    else:
        abuse_score = 0

    df = pd.DataFrame({
        "Metric": ["Abuse Confidence Score"],
        "Value": [abuse_score],
    })

    fig = px.bar(df, x="Metric", y="Value", color="Value",
                 title=f"Abuse Confidence Score for {ip_input} ({country})",
                 range_y=[0, 100], color_continuous_scale="Reds")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # ------------------- SAVE RESULTS -------------------
    import json, os
    save_path = os.path.join("data", f"enriched_{ip_input}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    os.makedirs("data", exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    st.success(f"📁 Results saved to {save_path}")

else:
    st.info("💡 Enter an IP above and click 'Analyze IP' to start.")
