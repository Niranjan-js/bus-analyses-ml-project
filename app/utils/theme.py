import streamlit as st

COLORS = {
    'primary': '#1B4F72',
    'secondary': '#2E86C1', 
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'critical': '#8E44AD',
    'text': '#2C3E50',
    'bg': '#F8F9FA',
    'card_bg': '#FFFFFF',
}

UTILIZATION_COLORS = {
    'Underutilized': '#3498DB',
    'Normal': '#27AE60',
    'High': '#F39C12',
    'Critical': '#E74C3C',
    'Over-capacity': '#8E44AD',
}

SEVERITY_COLORS = {
    'LOW': '#27AE60',
    'MEDIUM': '#F39C12', 
    'HIGH': '#E74C3C',
    'CRITICAL': '#8E44AD',
}

def apply_theme():
    """Apply modern visual theme via custom CSS."""
    custom_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        .stApp {{
            background-color: {COLORS['bg']};
            color: {COLORS['text']};
        }}
        div[data-testid="stMetric"] {{
            background-color: {COLORS['card_bg']};
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            border-top: 3px solid #1B4F72;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 14px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS['primary']};
            font-weight: 700;
        }}
        .stButton>button {{
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }}
        .stDownloadButton>button {{
            background-color: #1B4F72 !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
        }}
        .stDownloadButton>button:hover {{
            background-color: #2E86C1 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        }}
        .badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
