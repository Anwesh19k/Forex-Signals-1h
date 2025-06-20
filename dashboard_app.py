import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === MODEL IMPORTS ===
from one_hour import run_signal_engine as run_one_hour
from one_hour_pro import run_signal_engine as run_one_hour_pro
from one_hour_pro_plus import run_signal_engine as run_one_hour_pro_plus
from one_hour_pro_max_ai import run_signal_engine as run_one_hour_pro_max

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Forex Signal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === THEME ===
def set_custom_theme(mode):
    if mode == "Dark":
        st.markdown("""
            <style>
                body {
                    background-color: #0e1117;
                    color: #FFFFFF;
                }
                .stDataFrame thead tr th {
                    color: #FFFFFF;
                    background-color: #1c1c1c;
                }
                .stDataFrame tbody tr td {
                    background-color: #1c1c1c;
                    color: #FFFFFF;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .stDataFrame tbody tr td {
                    background-color: #FAFAFA;
                    color: #000000;
                }
            </style>
        """, unsafe_allow_html=True)

# === SIDEBAR: THEME + COUNTDOWN TIMER ===
st.markdown("### 🌗 Theme Settings")
theme_option = st.radio("Choose Theme Mode", ["Light", "Dark"], horizontal=True)

if theme_option == "Dark":
    st.markdown(
        """
        <style>
        .main { background-color: #0e1117; color: white; }
        .stDataFrame thead tr th { background-color: #1c1c1c; color: white; }
        .stDataFrame tbody tr td { background-color: #1c1c1c; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .main { background-color: #ffffff; color: black; }
        .stDataFrame tbody tr td { background-color: #fafafa; color: black; }
        </style>
        """,
        unsafe_allow_html=True
    )
# === Countdown to Next Hour ===
def time_until_next_hour():
    now = datetime.utcnow()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return next_hour - now

time_remaining = time_until_next_hour()
minutes, seconds = divmod(time_remaining.seconds, 60)
progress = (3600 - time_remaining.seconds) / 3600

st.sidebar.markdown("⏳ **Next Candle Countdown**")
st.sidebar.markdown(f"🕒 **{minutes:02}:{seconds:02}** remaining to next HH:00 candle")
st.sidebar.progress(progress)

# === Auto Refresh exactly at HH:00 ===
now = datetime.utcnow()
if now.minute == 0 and now.second <= 5:
    st.experimental_rerun()

# === TITLE ===
st.title("📊 Forex Signal Dashboard (1H, Pro, Pro+, and Pro Max)")
st.markdown("Get real-time signals from four AI models: **Standard**, **Pro**, **Pro+**, and **Pro Max AI**.")
st.caption("✅ Fully optimized for Desktop and Mobile screens.")

# === REFRESH BUTTON ===
highlight_refresh = now.minute >= 55
if highlight_refresh:
    st.markdown('<p style="color:orange; font-weight:bold;">⚠️ It\'s time to refresh the signals!</p>', unsafe_allow_html=True)

if st.button("🔄 Refresh Dashboards"):
    st.session_state['last_refreshed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.success("🔁 Dashboard refreshed!")
    st.rerun()

st.markdown(f"🕒 **Last Refreshed:** `{st.session_state.get('last_refreshed', 'Not yet refreshed')}`")

# === DASHBOARD TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["📘 1 Hour", "📗 Pro", "📙 Pro+", "🚀 Pro Max AI"])

with tab1:
    st.subheader("📘 1 Hour Model (Standard)")
    with st.spinner("🔄 Running 1 Hour model..."):
        df1 = run_one_hour()
    if not df1.empty:
        st.success(f"✅ {len(df1)} signals generated.")
        st.dataframe(df1, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")

with tab2:
    st.subheader("📗 1 Hour Model (Pro)")
    with st.spinner("🔄 Running 1 Hour Pro model..."):
        df2 = run_one_hour_pro()
    if not df2.empty:
        st.success(f"✅ {len(df2)} signals generated.")
        st.dataframe(df2, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")

with tab3:
    st.subheader("📙 1 Hour Model (Pro+)")
    with st.spinner("🔄 Running 1 Hour Pro+ model..."):
        df3 = run_one_hour_pro_plus()
    if not df3.empty:
        st.success(f"✅ {len(df3)} signals generated.")
        st.dataframe(df3, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")

with tab4:
    st.subheader("🚀 1 Hour Model (Pro Max AI Ensemble)")
    with st.spinner("🔄 Running 1 Hour Pro Max model..."):
        df4 = run_one_hour_pro_max()
    if not df4.empty:
        st.success(f"✅ {len(df4)} signals generated.")
        st.dataframe(df4, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")


