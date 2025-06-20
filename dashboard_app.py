import streamlit as st
import pandas as pd
from datetime import datetime

# === IMPORTS ===
from one_hour import run_signal_engine as run_one_hour
from one_hour_pro import run_signal_engine as run_one_hour_pro
from one_hour_pro_plus import run_signal_engine as run_one_hour_pro_plus
from one_hour_pro_max_ai import run_signal_engine as run_one_hour_pro_max

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
st.title("📊 Forex Signal Dashboard (1H, Pro, Pro+, and Pro Max)")
st.markdown("Get real-time signals from four AI models: **Standard**, **Pro**, **Pro+**, and **Pro Max**.")
st.caption("✅ Fully optimized for Desktop and Mobile screens.")

# === TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["📘 1 Hour", "📗 Pro", "📙 Pro+", "🚀 Pro Max with AI"])

with tab1:
    st.subheader("📘 1 Hour Model (Standard)")
    if st.button("🔄 Refresh 1H Model"):
        with st.spinner("🔄 Running 1 Hour model..."):
            st.session_state['df1'] = run_one_hour()
            st.session_state['last_refreshed_1'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df1 = st.session_state.get('df1', pd.DataFrame())
    if not df1.empty:
        st.success(f"✅ {len(df1)} signals generated.")
        st.dataframe(df1, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")
    st.markdown(f"🕒 **Last Refreshed (1H):** `{st.session_state.get('last_refreshed_1', 'Not yet refreshed')}`")

with tab2:
    st.subheader("📗 1 Hour Model (Pro)")
    if st.button("🔄 Refresh Pro Model"):
        with st.spinner("🔄 Running 1 Hour Pro model..."):
            st.session_state['df2'] = run_one_hour_pro()
            st.session_state['last_refreshed_2'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df2 = st.session_state.get('df2', pd.DataFrame())
    if not df2.empty:
        st.success(f"✅ {len(df2)} signals generated.")
        st.dataframe(df2, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")
    st.markdown(f"🕒 **Last Refreshed (Pro):** `{st.session_state.get('last_refreshed_2', 'Not yet refreshed')}`")

with tab3:
    st.subheader("📙 1 Hour Model (Pro+)")
    if st.button("🔄 Refresh Pro+ Model"):
        with st.spinner("🔄 Running 1 Hour Pro+ model..."):
            st.session_state['df3'] = run_one_hour_pro_plus()
            st.session_state['last_refreshed_3'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df3 = st.session_state.get('df3', pd.DataFrame())
    if not df3.empty:
        st.success(f"✅ {len(df3)} signals generated.")
        st.dataframe(df3, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")
    st.markdown(f"🕒 **Last Refreshed (Pro+):** `{st.session_state.get('last_refreshed_3', 'Not yet refreshed')}`")

with tab4:
    st.subheader("🚀 1 Hour Model (Pro Max Ensemble Voting)")
    if st.button("🔄 Refresh Pro Max AI"):
        with st.spinner("🔄 Running 1 Hour Pro Max model..."):
            st.session_state['df4'] = run_one_hour_pro_max()
            st.session_state['last_refreshed_4'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df4 = st.session_state.get('df4', pd.DataFrame())
    if not df4.empty:
        st.success(f"✅ {len(df4)} signals generated.")
        st.dataframe(df4, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated or model skipped.")
    st.markdown(f"🕒 **Last Refreshed (Pro Max):** `{st.session_state.get('last_refreshed_4', 'Not yet refreshed')}`")


