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
    def render_sidebar_uploader(): pass

from utils.analytics import (
    compute_bus_utilization, compute_delay_analysis,
    compute_complaint_analysis, compute_kpis
)
from utils.theme import apply_theme
from ai.chat import ask_transport_ai

st.set_page_config(page_title="Ask Transport AI", page_icon="💬", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("💬 Ask Transport AI")
st.markdown("*Ask natural language questions about the college transportation system. All answers are generated from actual data.*")
st.divider()

data = load_data()
bus_util = compute_bus_utilization(data['bus_usage'], data['buses'])
delay_df = compute_delay_analysis(data['bus_usage'], data['buses'])
cat_dist, complaints_by_bus, comp_trend = compute_complaint_analysis(data['complaints'], data['buses'])
kpis = compute_kpis(data['students'], data['buses'], data['stops'], data['bus_usage'], data['complaints'])

analytics_results = {
    'bus_utilization': bus_util,
    'delay_analysis': delay_df,
    'complaint_categories': cat_dist,
    'complaints_by_bus': complaints_by_bus,
    'kpis': kpis
}

st.subheader("🚀 Quick Questions")
preset_questions = [
    "Which bus is most crowded?",
    "Which route has the most delays?",
    "What are the top complaint categories?",
    "Which bus is underutilized?",
    "Which department uses transport the most?",
    "Which stop has the most students?",
    "What should management do?",
    "Give me a system summary",
    "Why is B03 high risk?"
]

cols = st.columns(3)
selected_preset = None
for i, q in enumerate(preset_questions):
    with cols[i % 3]:
        if st.button(q, key=f"preset_{i}", use_container_width=True):
            selected_preset = q

st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_question = selected_preset or st.chat_input("Ask a question about the transport data...")

if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    result = ask_transport_ai(user_question, data, analytics_results)
    
    response_parts = []
    response_parts.append(f"**{result['answer']}**")
    
    if result.get('evidence'):
        response_parts.append(f"\n📊 **Evidence:** {result['evidence']}")
    
    if result.get('recommendation'):
        response_parts.append(f"\n💡 **Recommendation:** {result['recommendation']}")
    
    full_response = "\n".join(response_parts)
    
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant"):
        st.markdown(full_response)

with st.sidebar:
    st.subheader("💡 Example Questions")
    st.markdown("""
    - Which bus is most crowded?
    - Which route has the most delays?
    - What are the top complaints?
    - Why is B03 high risk?
    - What should management do?
    - Which bus is underutilized?
    - Which department uses transport most?
    - How many students use B01?
    - Which stop has most students?
    - Give me a summary
    """)
