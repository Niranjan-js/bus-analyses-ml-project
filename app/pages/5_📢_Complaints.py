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
    def render_sidebar_uploader():
        pass

from utils.theme import apply_theme
from utils.reports import generate_csv_download

st.set_page_config(page_title="Complaints Analysis", page_icon="📢", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("📢 Complaints Analysis & Audit")
st.markdown("*Comprehensive complaint tracking, category distribution, severity analysis, and raw log export.*")
st.divider()

data = load_data()
complaints = data['complaints']

if complaints.empty:
    st.success("No complaints found in the system!")
    st.stop()

# Key Complaint Metrics Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Complaints", len(complaints))
top_cat = complaints['category'].value_counts().index[0]
c2.metric("Top Complaint Category", top_cat)
top_bus = complaints['bus_id'].value_counts().index[0]
c3.metric("Highest Complaint Bus", top_bus)
c4.metric("Categories Count", complaints['category'].nunique())

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Complaints by Category")
    cat_counts = complaints['category'].value_counts().reset_index()
    cat_counts.columns = ['category', 'count']
    fig1 = px.pie(cat_counts, names='category', values='count', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Complaints by Bus")
    bus_counts = complaints['bus_id'].value_counts().reset_index()
    bus_counts.columns = ['bus_id', 'count']
    fig2 = px.bar(bus_counts, x='bus_id', y='count', color='count', color_continuous_scale='Reds', labels={'count': 'Complaints', 'bus_id': 'Bus ID'})
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Complaint Timeline Trend")
complaints['date'] = pd.to_datetime(complaints['date'])
trend = complaints.groupby('date').size().reset_index(name='count')
fig3 = px.line(trend, x='date', y='count', markers=True, title="Daily Complaints Frequency")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("📋 Complaint Log Filter & Download")
category_filter = st.multiselect("Filter by Category", options=complaints['category'].unique())
filtered_comps = complaints if not category_filter else complaints[complaints['category'].isin(category_filter)]

col_table, col_down = st.columns([3, 1])
with col_table:
    st.dataframe(filtered_comps, use_container_width=True, hide_index=True)

with col_down:
    st.markdown("#### Export Log")
    generate_csv_download(filtered_comps, "Complaints_Filtered_Export.csv", label="📥 Download Complaints CSV")
