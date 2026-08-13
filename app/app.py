import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.data_loader import load_data, render_sidebar_uploader
except ImportError:
    from utils.data_loader import load_data
    def render_sidebar_uploader():
        pass

from utils.analytics import compute_kpis, compute_bus_utilization, compute_delay_analysis
from utils.theme import apply_theme, COLORS

st.set_page_config(
    page_title="🚌 AI College Transport Analyzer",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar_uploader()

# Load data
data = load_data()
kpis = compute_kpis(data['students'], data['buses'], data['stops'], data['bus_usage'], data['complaints'])

# Title
st.markdown("<h1 style='text-align: center; color: #1B4F72;'>🚌 AI College Transport Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5D6D7E; font-size: 1.2em;'>AI-Powered Transportation Intelligence for College Management</p>", unsafe_allow_html=True)
st.divider()

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Students", kpis.get('total_students', 120))
col2.metric("Total Buses", kpis.get('total_buses', 6))
col3.metric("Avg Utilization", f"{kpis.get('avg_utilization', 75.0):.1f}%")
col4.metric("Delayed Trips", kpis.get('delayed_trips', 12))
col5.metric("Total Complaints", kpis.get('total_complaints', 90))

# System Health
health = kpis.get('system_health', 'ATTENTION')
health_emoji = {'HEALTHY': '🟢', 'ATTENTION': '🟠', 'CRITICAL': '🔴'}.get(health, '🟠')
st.markdown(f"### System Health: {health_emoji} {health}")

# Quick overview charts in 2 columns
col1, col2 = st.columns(2)
with col1:
    st.subheader("Bus Utilization Overview")
    util = compute_bus_utilization(data['bus_usage'], data['buses'])
    if not util.empty:
        fig1 = px.bar(
            util, x='bus_id', y='utilization_pct', 
            title="Avg Utilization by Bus (%)", 
            color='utilization_pct',
            color_continuous_scale='YlOrRd',
            labels={'utilization_pct': 'Utilization %', 'bus_id': 'Bus ID'}
        )
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Complaints Breakdown")
    comp = data['complaints']
    if not comp.empty:
        fig2 = px.pie(comp, names='category', title="Complaints by Category", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

st.info("👈 Use the sidebar to navigate to detailed analytics, AI insights, and predictions.")
