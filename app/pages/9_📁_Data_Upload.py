import streamlit as st
import pandas as pd
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

st.set_page_config(page_title="Data Management & Upload", page_icon="📁", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("📁 Data Management & CSV Upload")
st.markdown("*Upload custom CSV files to test the AI College Transport Analyzer with new or updated datasets.*")
st.divider()

if 'custom_data' not in st.session_state:
    st.session_state['custom_data'] = {}

# Current Data Status
active_source = "Custom Uploaded CSVs" if st.session_state.get('custom_data') else "Default Dataset / Snowflake"
st.info(f"**Current Active Data Source:** {active_source}")

st.subheader("📤 Upload Custom CSV Datasets")
st.markdown("You can upload any of the 5 CSV datasets below. All analytics, AI insights, predictions, and chatbot responses will instantly adapt to your uploaded data!")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1. Students Dataset (`students.csv`)")
    st.caption("Required columns: `student_id`, `name`, `department`, `year`, `bus_id`, `stop_id`")
    f_students = st.file_uploader("Upload students.csv", type=["csv"], key="pg_students")
    if f_students:
        df = pd.read_csv(f_students)
        st.session_state['custom_data']['students'] = df
        st.success(f"Loaded {len(df)} students successfully!")
        
    st.markdown("#### 2. Buses Dataset (`buses.csv`)")
    st.caption("Required columns: `bus_id`, `route`, `total_capacity`, `driver`")
    f_buses = st.file_uploader("Upload buses.csv", type=["csv"], key="pg_buses")
    if f_buses:
        df = pd.read_csv(f_buses)
        st.session_state['custom_data']['buses'] = df
        st.success(f"Loaded {len(df)} buses successfully!")

    st.markdown("#### 3. Stops Dataset (`stops.csv`)")
    st.caption("Required columns: `stop_id`, `stop_name`, `area`, `distance_km`")
    f_stops = st.file_uploader("Upload stops.csv", type=["csv"], key="pg_stops")
    if f_stops:
        df = pd.read_csv(f_stops)
        st.session_state['custom_data']['stops'] = df
        st.success(f"Loaded {len(df)} stops successfully!")

with col2:
    st.markdown("#### 4. Bus Usage Dataset (`bus_usage.csv`)")
    st.caption("Required columns: `date`, `bus_id`, `students_boarded`, `arrival_time`, `departure_time`, `delay_minutes`")
    f_usage = st.file_uploader("Upload bus_usage.csv", type=["csv"], key="pg_bus_usage")
    if f_usage:
        df = pd.read_csv(f_usage)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        st.session_state['custom_data']['bus_usage'] = df
        st.success(f"Loaded {len(df)} bus usage records successfully!")

    st.markdown("#### 5. Complaints Dataset (`complaints.csv`)")
    st.caption("Required columns: `complaint_id`, `date`, `bus_id`, `student_id`, `category`, `description`")
    f_complaints = st.file_uploader("Upload complaints.csv", type=["csv"], key="pg_complaints")
    if f_complaints:
        df = pd.read_csv(f_complaints)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        st.session_state['custom_data']['complaints'] = df
        st.success(f"Loaded {len(df)} complaints successfully!")

st.divider()

# Reset button
col_a, col_b = st.columns([1, 4])
with col_a:
    if st.button("🔄 Reset to Default Data", use_container_width=True):
        st.session_state['custom_data'] = {}
        st.rerun()

st.subheader("🔍 Preview Active Datasets")
data = load_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Students", "Buses", "Stops", "Bus Usage", "Complaints"])

with tab1:
    st.dataframe(data['students'], use_container_width=True)

with tab2:
    st.dataframe(data['buses'], use_container_width=True)

with tab3:
    st.dataframe(data['stops'], use_container_width=True)

with tab4:
    st.dataframe(data['bus_usage'], use_container_width=True)

with tab5:
    st.dataframe(data['complaints'], use_container_width=True)
