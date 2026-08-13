import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

try:
    from utils.data_loader import load_data, render_sidebar_uploader
except ImportError:
    from utils.data_loader import load_data
    def render_sidebar_uploader(): pass

from utils.theme import apply_theme

st.set_page_config(page_title="Route Analytics", page_icon="🛣️", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("🛣️ Route Analytics")

data = load_data()
buses = data['buses']
usage = data['bus_usage']
merged = pd.merge(usage, buses, on='bus_id')

st.subheader("Route Performance")
route_perf = merged.groupby('route').agg(
    avg_delay=('delay_minutes', 'mean'),
    avg_load=('students_boarded', 'mean'),
    max_load=('students_boarded', 'max'),
    capacity=('total_capacity', 'first')
).reset_index()

route_perf['utilization'] = (route_perf['avg_load'] / route_perf['capacity']) * 100

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(route_perf, x='route', y='utilization', title="Average Route Utilization (%)", color='utilization', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.scatter(route_perf, x='utilization', y='avg_delay', text='route', size='capacity', color='route', title="Utilization vs Delay by Route")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Route Health & Details")
st.dataframe(route_perf, use_container_width=True, hide_index=True)
