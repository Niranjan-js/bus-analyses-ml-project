import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from utils.data_loader import load_data
from utils.theme import apply_theme

st.set_page_config(page_title="Stop Analytics", page_icon="📍", layout="wide")
apply_theme()

st.title("📍 Stop Analytics")

data = load_data()
students = data['students']
stops = data['stops']

st.subheader("Students per Stop")
stop_counts = students['stop_id'].value_counts().reset_index()
stop_counts.columns = ['stop_id', 'student_count']
stop_data = pd.merge(stop_counts, stops, on='stop_id')

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(stop_data, x='stop_name', y='student_count', title="Student Count by Stop", color='area')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.scatter(stop_data, x='distance_km', y='student_count', hover_name='stop_name', color='area', size='student_count', title="Distance vs Students")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Area-wise Distribution")
area_counts = stop_data.groupby('area')['student_count'].sum().reset_index()
fig3 = px.pie(area_counts, names='area', values='student_count', title="Students by Area", hole=0.4)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Stop Detail Table")
st.dataframe(stop_data.drop(columns=['stop_id']), use_container_width=True)
