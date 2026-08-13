import os
import pandas as pd
import streamlit as st
from pathlib import Path
import logging

try:
    import snowflake.connector
except ImportError:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

def get_snowflake_connection():
    """Get Snowflake connection if env vars are present."""
    required_vars = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA", "SNOWFLAKE_WAREHOUSE"
    ]
    if all(os.getenv(v) for v in required_vars):
        try:
            conn = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
            )
            return conn
        except Exception as e:
            logging.error(f"Snowflake connection failed: {e}")
    return None

def load_data():
    """Load all required datasets.
    
    Priority order:
    1. Session state uploaded data (if user uploaded custom CSVs)
    2. Live Snowflake connection (if env vars set)
    3. Fallback to local CSV files in data/
    """
    data = {}
    
    # 1. Check if user uploaded custom data via Streamlit UI
    if 'custom_data' in st.session_state and st.session_state['custom_data']:
        data = st.session_state['custom_data'].copy()
        # Fill missing tables from CSV defaults if partially uploaded
        default_data = _load_default_csv_data()
        for key in ["students", "buses", "stops", "bus_usage", "complaints"]:
            if key not in data or data[key] is None or data[key].empty:
                data[key] = default_data[key]
        return data

    # 2. Try Snowflake connection
    conn = get_snowflake_connection()
    if conn:
        try:
            tables = {
                "students": "students",
                "buses": "buses",
                "stops": "stops",
                "bus_usage": "bus_usage",
                "complaints": "complaints"
            }
            for key, table in tables.items():
                query = f"SELECT * FROM {table}"
                data[key] = pd.read_sql(query, conn)
                data[key].columns = [c.lower() for c in data[key].columns]
            conn.close()
            
            # Format dates
            if 'date' in data.get('bus_usage', pd.DataFrame()).columns:
                data['bus_usage']['date'] = pd.to_datetime(data['bus_usage']['date'])
            if 'date' in data.get('complaints', pd.DataFrame()).columns:
                data['complaints']['date'] = pd.to_datetime(data['complaints']['date'])
                
            return data
        except Exception as e:
            logging.error(f"Error reading from Snowflake: {e}. Falling back to local CSV.")

    # 3. Fallback to default local CSV files
    return _load_default_csv_data()

def _load_default_csv_data():
    """Helper to load default local CSVs."""
    data = {}
    try:
        data["students"] = pd.read_csv(DATA_DIR / "students.csv")
        data["buses"] = pd.read_csv(DATA_DIR / "buses.csv")
        data["stops"] = pd.read_csv(DATA_DIR / "stops.csv")
        data["bus_usage"] = pd.read_csv(DATA_DIR / "bus_usage.csv")
        data["complaints"] = pd.read_csv(DATA_DIR / "complaints.csv")
        
        # Convert date columns
        if 'date' in data['bus_usage'].columns:
            data['bus_usage']['date'] = pd.to_datetime(data['bus_usage']['date'])
        if 'date' in data['complaints'].columns:
            data['complaints']['date'] = pd.to_datetime(data['complaints']['date'])
            
    except Exception as e:
        logging.error(f"Error reading default CSV files: {e}")
        raise e
        
    return data

def render_sidebar_uploader():
    """Renders a collapsible CSV file uploader in the Streamlit sidebar."""
    with st.sidebar.expander("📁 Upload Custom CSV Inputs", expanded=False):
        st.markdown("*Upload custom CSV files to override default datasets:*")
        
        if 'custom_data' not in st.session_state:
            st.session_state['custom_data'] = {}
            
        up_students = st.file_uploader("students.csv", type=["csv"], key="side_students")
        up_buses = st.file_uploader("buses.csv", type=["csv"], key="side_buses")
        up_stops = st.file_uploader("stops.csv", type=["csv"], key="side_stops")
        up_usage = st.file_uploader("bus_usage.csv", type=["csv"], key="side_bus_usage")
        up_complaints = st.file_uploader("complaints.csv", type=["csv"], key="side_complaints")
        
        updated = False
        if up_students:
            st.session_state['custom_data']['students'] = pd.read_csv(up_students)
            updated = True
        if up_buses:
            st.session_state['custom_data']['buses'] = pd.read_csv(up_buses)
            updated = True
        if up_stops:
            st.session_state['custom_data']['stops'] = pd.read_csv(up_stops)
            updated = True
        if up_usage:
            df_u = pd.read_csv(up_usage)
            if 'date' in df_u.columns:
                df_u['date'] = pd.to_datetime(df_u['date'])
            st.session_state['custom_data']['bus_usage'] = df_u
            updated = True
        if up_complaints:
            df_c = pd.read_csv(up_complaints)
            if 'date' in df_c.columns:
                df_c['date'] = pd.to_datetime(df_c['date'])
            st.session_state['custom_data']['complaints'] = df_c
            updated = True
            
        if updated:
            st.success("✅ Custom data active!")
            
        if st.session_state.get('custom_data'):
            if st.button("🔄 Reset to Default Data", key="side_reset"):
                st.session_state['custom_data'] = {}
                st.rerun()
