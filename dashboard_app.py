import streamlit as st
import pandas as pd
from datetime import datetime

# === IMPORTS ===
from one_hour import run_signal_engine as run_one_hour
from one_hour_pro import run_signal_engine as run_one_hour_pro
from one_hour_pro_plus import run_signal_engine as run_one_hour_pro_plus  # Make sure this exists

# === CONFIG ===
st.set_page_config(
    page_title="Forex Signal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === THEME CSS ===
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

# === SIDEBAR ===
mode = st.sidebar.radio("🌗 Theme Mode", ["Light", "Dark"], index=0)
set_custom_theme(mode)

# === TITLE ===
st.title("📊 Forex Signal Dashboard (1H, Pro & Pro+)")
st.markdown("Get real-time signals from three AI models: **Standard**, **Pro**, and **Pro+**.")
st.caption("✅ Fully optimized for Desktop and Mobile screens.")

# === REFRESH BUTTON ===
if st.button("🔄 Refresh Dashboards"):
    st.session_state['last_refreshed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.success("🔁 Dashboard refreshed!")
    st.rerun()


st.markdown(f"🕒 **Last Refreshed:** `{st.session_state.get('last_refreshed', 'Not yet refreshed')}`")

# === TABS ===
tab1, tab2, tab3 = st.tabs(["📘 1 Hour Model", "📗 1 Hour Pro", "📙 1 Hour Pro+"])


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
