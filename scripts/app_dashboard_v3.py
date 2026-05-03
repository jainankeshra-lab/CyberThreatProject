import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
from scripts.fetch_multi_threats import enrich_ip

st.set_page_config(page_title="Cyber Threat Intelligence Dashboard", page_icon="🛡️", layout="wide")

# -------------------------------------------------------------
# 🎯 Header
# -------------------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#00adb5;'>🛡️ Cyber Threat Intelligence Dashboard</h1>
<p style='text-align:center; color:gray;'>Live Threat Insights from AbuseIPDB, AlienVault OTX & ThreatCrowd</p>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 🧾 User input section
# -------------------------------------------------------------
ip_input = st.text_input("🔍 Enter an IP address to analyze:", placeholder="e.g., 8.8.8.8")

if ip_input:
    with st.spinner("Fetching live threat intelligence... ⏳"):
        data = enrich_ip(ip_input)
        st.success(f"✅ Enrichment complete for {ip_input}")
    
    # Display raw view toggle
    with st.expander("🧩 Raw API Data (for experts)"):
        st.json(data)
    
    # -------------------------------------------------------------
    # 🧠 Parsed summary
    # -------------------------------------------------------------
    st.markdown("### 🌐 Threat Intelligence Summary")
    
    abuse_data = data["sources"].get("abuseipdb", {})
    otx_data = data["sources"].get("otx", {})
    tc_data = data["sources"].get("threatcrowd", {})

    col1, col2, col3 = st.columns(3)

    # --- AbuseIPDB Summary ---
    with col1:
        st.subheader("🚨 AbuseIPDB")
        if "error" in abuse_data:
            st.error(f"❌ {abuse_data['error']}")
        else:
            score = abuse_data.get("abuseConfidenceScore", 0)
            total = abuse_data.get("totalReports", 0)
            users = abuse_data.get("numDistinctUsers", 0)
            last_seen = abuse_data.get("lastReportedAt", "N/A")
            risk_level = (
                "🟢 Low Risk" if score < 20 else
                "🟡 Moderate Risk" if score < 60 else
                "🔴 High Risk"
            )
            st.metric("Abuse Confidence Score", f"{score}/100", risk_level)
            st.write(f"**Country:** {abuse_data.get('countryCode', 'Unknown')}")
            st.write(f"**Usage Type:** {abuse_data.get('usageType', 'N/A')}")
            st.write(f"**ISP:** {abuse_data.get('isp', 'N/A')}")
            st.write(f"**Domain:** {abuse_data.get('domain', 'N/A')}")
            st.write(f"**Total Reports:** {total} from {users} users")
            st.write(f"**Last Seen:** {last_seen}")

    # --- AlienVault OTX Summary ---
    with col2:
        st.subheader("👽 AlienVault OTX")
        if "error" in otx_data:
            st.error(f"❌ {otx_data['error']}")
        else:
            rep = otx_data.get("reputation", 0)
            st.metric("Reputation", rep)
            base = otx_data.get("base_indicator", {})
            st.write(f"**Indicator Type:** {base.get('type', 'Unknown')}")
            st.write(f"**Access Type:** {base.get('access_type', 'N/A')}")
            whois = otx_data.get("whois")
            if whois:
                st.write(f"**WHOIS:** [{whois}]({whois})")

    # --- ThreatCrowd Summary ---
    with col3:
        st.subheader("🌩️ ThreatCrowd")
        if "error" in tc_data:
            st.warning(f"⚠️ {tc_data['error']}")
        else:
            st.write(f"**Votes:** {tc_data.get('votes', 'N/A')}")
            st.write(f"**Reports:** {tc_data.get('reports', 'N/A')}")
            st.write(f"**Domains:** {len(tc_data.get('domains', []))} linked domains")

    # -------------------------------------------------------------
    # 📊 Analytics Graphs
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📈 Visual Analytics")

    abuse_score = abuse_data.get("abuseConfidenceScore", None)
    total_reports = abuse_data.get("totalReports", None)
    num_users = abuse_data.get("numDistinctUsers", None)

    if abuse_score is not None:
        df_plot = pd.DataFrame({
            "Metric": ["Abuse Confidence", "Reports", "Unique Users"],
            "Value": [abuse_score, total_reports or 0, num_users or 0]
        })

        fig = px.bar(df_plot, x="Metric", y="Value", color="Metric",
                     title="AbuseIPDB Threat Metrics Overview",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No numerical data available for chart visualization.")
else:
    st.info("👆 Enter an IP address above to begin analysis.")
