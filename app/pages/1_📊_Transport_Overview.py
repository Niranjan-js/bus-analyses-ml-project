import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from utils.data_loader import load_data
from utils.analytics import compute_kpis, compute_bus_utilization, compute_delay_analysis, compute_daily_trends
from utils.theme import apply_theme

st.set_page_config(page_title="Transport Overview", page_icon="📊", layout="wide")
apply_theme()

st.title("📊 Transport Overview")

data = load_data()
kpis = compute_kpis(data['students'], data['buses'], data['stops'], data['bus_usage'], data['complaints'])

# KPI metrics row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", kpis.get('total_students', 120))
c2.metric("Avg Bus Utilization", f"{kpis.get('avg_utilization', 75):.1f}%")
c3.metric("Delayed Trips", kpis.get('delayed_trips', 12))
c4.metric("Complaints", kpis.get('total_complaints', 90))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bus Utilization")
    util = compute_bus_utilization(data['bus_usage'], data['buses'])
    if not util.empty:
        fig1 = px.bar(
            util, x='utilization_pct', y='bus_id', orientation='h', 
            color='category', title="Utilization by Bus (%)",
            labels={'utilization_pct': 'Utilization %', 'bus_id': 'Bus ID'}
        )
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Route Performance")
    # Join buses and usage
    bu = data['bus_usage'].merge(data['buses'], on='bus_id')
    route_perf = bu.groupby('route').agg({'delay_minutes': 'mean', 'students_boarded': 'mean'}).reset_index()
    if not route_perf.empty:
        fig2 = px.bar(
            route_perf, x='route', y=['delay_minutes', 'students_boarded'], 
            barmode='group', title="Route Delay vs Average Load",
            labels={'value': 'Count / Minutes', 'route': 'Route'}
        )
        st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Daily Delay Trend")
    daily = compute_daily_trends(data['bus_usage'], data['buses'])
    if not daily.empty:
        fig3 = px.line(daily, x='date', y='avg_delay', title="Average Daily Delay (Minutes)", markers=True)
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Complaints Categories")
    comps = data['complaints']
    if not comps.empty:
        fig4 = px.pie(comps, names='category', hole=0.3, title="Complaint Distribution")
        st.plotly_chart(fig4, use_container_width=True)
