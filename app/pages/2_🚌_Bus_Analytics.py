import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

try:
    from utils.data_loader import load_data, render_sidebar_uploader
except ImportError:
    from utils.data_loader import load_data
    def render_sidebar_uploader(): pass

from utils.analytics import compute_bus_utilization
from utils.theme import apply_theme

st.set_page_config(page_title="Bus Analytics", page_icon="🚌", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("🚌 Detailed Bus Analytics")

data = load_data()
buses = data['buses']
bus_usage = data['bus_usage']
complaints = data['complaints']

# Selector
selected_bus = st.selectbox("Select a Bus to Analyze", options=["All"] + list(buses['bus_id'].unique()))

util = compute_bus_utilization(bus_usage, buses)

st.subheader("System Wide Utilization")
if not util.empty:
    fig_util = px.bar(
        util, x='bus_id', y='utilization_pct', 
        title="Utilization Across Fleet (%)",
        color='category',
        labels={'utilization_pct': 'Utilization %', 'bus_id': 'Bus ID'}
    )
    fig_util.add_hline(y=40, line_dash="dash", line_color="blue", annotation_text="Under 40%")
    fig_util.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Optimal 70%")
    fig_util.add_hline(y=85, line_dash="dash", line_color="orange", annotation_text="Near Cap 85%")
    fig_util.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Overcrowded 100%")
    st.plotly_chart(fig_util, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Bus Details")
    filtered_buses = buses if selected_bus == "All" else buses[buses['bus_id'] == selected_bus]
    st.dataframe(filtered_buses, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Utilization vs Complaints")
    comp_counts = complaints.groupby('bus_id').size().reset_index(name='complaints')
    scatter_data = pd.merge(util, comp_counts, on='bus_id', how='left').fillna({'complaints': 0})
    fig_scat = px.scatter(
        scatter_data, x='utilization_pct', y='complaints', color='bus_id', size='total_capacity',
        title="Utilization vs Complaints Correlation",
        labels={'utilization_pct': 'Utilization %', 'complaints': 'Complaint Count'}
    )
    st.plotly_chart(fig_scat, use_container_width=True)

if selected_bus != "All":
    st.subheader(f"Daily Utilization Trend for {selected_bus}")
    usage_bus = bus_usage[bus_usage['bus_id'] == selected_bus].copy()
    bus_cap = buses[buses['bus_id'] == selected_bus]['total_capacity'].values[0]
    usage_bus['utilization_pct'] = (usage_bus['students_boarded'] / bus_cap) * 100
    fig_trend = px.line(
        usage_bus, x='date', y='utilization_pct', 
        title=f"{selected_bus} Daily Utilization (%)",
        labels={'utilization_pct': 'Utilization %', 'date': 'Date'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)
