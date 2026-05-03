import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as _dt
from pathlib import Path

# -------------------------------------------------------------

#  App Configuration

# -------------------------------------------------------------

st.set_page_config(
page_title="Cyber Threat Intelligence Dashboard",
page_icon="🛡️",
layout="wide",
)

st.title("🛡️ Cyber Threat Intelligence Dashboard")
st.markdown("### Monitor, Analyze & Predict Malicious IP Activity")

# -------------------------------------------------------------

#  Load Data

# -------------------------------------------------------------




DATA_PATH = Path("data")
json_files = sorted(DATA_PATH.glob("*.json"), reverse=True)




if not json_files:
st.error("No data files found in the data folder. Please fetch data first.")
st.stop()
else:
latest_file = json_files[0]
st.sidebar.success(f"Loaded data: {latest_file.name}")
df = pd.read_json(latest_file)

# -------------------------------------------------------------

#  Data Preprocessing

# -------------------------------------------------------------

if "lastReportedAt" in df.columns:
df["lastReportedAt"] = pd.to_datetime(df["lastReportedAt"], errors="coerce", utc=True)
else:
st.error("The dataset is missing 'lastReportedAt' field.")
st.stop()

# Handle missing or malformed columns gracefully

for col in ["countryCode", "abuseConfidenceScore"]:
if col not in df.columns:
df[col] = None

# -------------------------------------------------------------

#  Sidebar Filters

# -------------------------------------------------------------

st.sidebar.header("🔎 Filters")




country_list = sorted(df["countryCode"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", ["All"] + country_list)




days_filter = st.sidebar.selectbox(
"Filter by Time Range",
["Any", "7 days", "30 days", "90 days"]
)

-------------------------------------------------------------
#🕒 Date Filtering
-------------------------------------------------------------



df_view = df.copy()




if days_filter != "Any":
days_map = {"7 days": 7, "30 days": 30, "90 days": 90}
now_utc = _dt.datetime.now(_dt.timezone.utc)
cutoff = pd.Timestamp(now_utc) - pd.Timedelta(days=days_map[days_filter])
df_view = df_view[df_view["lastReportedAt"] >= cutoff]




if selected_country != "All":
df_view = df_view[df_view["countryCode"] == selected_country]

-------------------------------------------------------------
#📊 Metrics
-------------------------------------------------------------



total_reports = len(df_view)
unique_ips = df_view["ipAddress"].nunique() if "ipAddress" in df_view.columns else 0
avg_confidence = round(df_view["abuseConfidenceScore"].mean(), 2) if total_reports > 0 else 0




col1, col2, col3 = st.columns(3)
col1.metric("📡 Total Reports", f"{total_reports}")
col2.metric("🌐 Unique IPs", f"{unique_ips}")
col3.metric("🔥 Avg. Confidence Score", f"{avg_confidence}")

-------------------------------------------------------------
#📈 Graphs and Visualizations
-------------------------------------------------------------



st.markdown("## 📊 Threat Intelligence Insights")




if total_reports == 0:
st.warning("No data available for the selected filters.")
st.stop()

Histogram of Confidence Scores



fig_conf = px.histogram(
df_view,
x="abuseConfidenceScore",
nbins=20,
title="Abuse Confidence Score Distribution",
color_discrete_sequence=["#007BFF"],
)
st.plotly_chart(fig_conf, use_container_width=True)

Country-based threat counts



if "countryCode" in df_view.columns:
top_countries = (
df_view["countryCode"]
.value_counts()
.reset_index()
.rename(columns={"index": "Country", "countryCode": "Count"})
)
fig_country = px.bar(
top_countries.head(10),
x="Country",
y="Count",
title="Top Countries Reporting Malicious IPs",
color="Count",
color_continuous_scale="Reds",
)
st.plotly_chart(fig_country, use_container_width=True)

Time-based trends



if "lastReportedAt" in df_view.columns:
df_time = df_view.copy()
df_time["date"] = df_time["lastReportedAt"].dt.date
time_trend = df_time.groupby("date").size().reset_index(name="Reports")

fig_trend = px.line(
    time_trend,
    x="date",
    y="Reports",
    title="📅 Daily Malicious IP Reports Trend",
    markers=True,
)
st.plotly_chart(fig_trend, use_container_width=True)

-------------------------------------------------------------
#🔎 Data Table
-------------------------------------------------------------



st.markdown("### 🧾 Detailed Report Data")
st.dataframe(
df_view[["ipAddress", "countryCode", "abuseConfidenceScore", "lastReportedAt"]],
use_container_width=True,
)

-------------------------------------------------------------
#🕵️ User Interaction
-------------------------------------------------------------



st.markdown("---")
st.markdown("#### 🔍 Check IP Reputation")




ip_query = st.text_input("Enter an IP Address:")
if ip_query:
ip_data = df[df["ipAddress"] == ip_query]
if not ip_data.empty:
ip_row = ip_data.iloc[0]
st.success(f"✅ IP {ip_query} found in dataset.")
st.json(ip_row.to_dict())
else:
st.warning(f"No data found for IP {ip_query}.")

-------------------------------------------------------------
#✅ Footer
-------------------------------------------------------------



st.markdown("---")
st.caption("Developed by Ankeshra and Team | Cyber Threat Intelligence Project")
