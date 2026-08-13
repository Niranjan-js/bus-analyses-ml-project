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

from utils.analytics import (
    compute_bus_utilization, compute_delay_analysis,
    compute_complaint_analysis, compute_kpis
)
from utils.theme import apply_theme, SEVERITY_COLORS
from ai.insights import generate_bus_insights, generate_system_summary

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("🤖 AI Transport Intelligence")
st.markdown("*AI-powered analysis of transportation data with evidence-based recommendations*")
st.divider()

data = load_data()
kpis = compute_kpis(data['students'], data['buses'], data['stops'], data['bus_usage'], data['complaints'])
bus_util = compute_bus_utilization(data['bus_usage'], data['buses'])
delay_df = compute_delay_analysis(data['bus_usage'], data['buses'])
_, complaints_by_bus, _ = compute_complaint_analysis(data['complaints'], data['buses'])

# Generate AI insights
bus_insights = generate_bus_insights(bus_util, delay_df, complaints_by_bus)
system_summary = generate_system_summary(kpis, bus_insights)

# System Health Banner
health = system_summary['health_status']
health_colors = {'Good': '#27AE60', 'Fair': '#F39C12', 'Critical': '#E74C3C'}
health_emojis = {'Good': '🟢', 'Fair': '🟠', 'Critical': '🔴'}
st.markdown(
    f"""<div style='background-color: {health_colors.get(health, '#F39C12')}20; 
    border-left: 5px solid {health_colors.get(health, '#F39C12')}; 
    padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
    <h3>{health_emojis.get(health, '🟠')} System Health: {health}</h3>
    <p>{system_summary['key_findings']}</p>
    </div>""", unsafe_allow_html=True
)

# Priority Actions
if system_summary['priority_actions']:
    st.subheader("⚡ Priority Actions")
    for action in system_summary['priority_actions']:
        st.warning(action)

# Top Risks
if system_summary['top_risks']:
    st.subheader("🚨 Top Risks")
    for risk in system_summary['top_risks']:
        st.error(risk)

st.divider()

# Bus Risk Scores
st.subheader("📊 Bus Risk Assessment")

# Sort insights by risk score (highest first)
sorted_insights = sorted(bus_insights, key=lambda x: x['risk_score'], reverse=True)

for insight in sorted_insights:
    severity = insight['severity']
    color = SEVERITY_COLORS.get(severity, '#F39C12')
    emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}.get(severity, '🟡')
    
    with st.expander(
        f"{emoji} Bus {insight['bus_id']} ({insight['route']}) — "
        f"Risk Score: {insight['risk_score']}/100 [{severity}]",
        expanded=(severity in ['HIGH', 'CRITICAL'])
    ):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risk Score", f"{insight['risk_score']}/100")
        col2.metric("Utilization", f"{insight['evidence']['utilization']:.1f}%")
        col3.metric("Avg Delay", f"{insight['evidence']['avg_delay']:.1f} min")
        col4.metric("Complaints", int(insight['evidence']['complaints']))
        
        # Progress bar for risk
        st.progress(min(insight['risk_score'] / 100, 1.0))
        
        if insight['problems']:
            st.markdown("**🔍 Detected Problems:**")
            for problem in insight['problems']:
                st.markdown(f"- ⚠️ {problem}")
        else:
            st.markdown("**✅ No significant issues detected.**")
        
        st.markdown(f"**💡 Recommendation:** {insight['recommendation']}")
        st.markdown(f"**📈 Expected Impact:** {insight['expected_impact']}")

st.divider()

# AI Recommendations Summary
st.subheader("📋 Management Action Plan")

critical_buses = [i for i in sorted_insights if i['severity'] == 'CRITICAL']
high_buses = [i for i in sorted_insights if i['severity'] == 'HIGH']
medium_buses = [i for i in sorted_insights if i['severity'] == 'MEDIUM']

if critical_buses:
    st.error(f"🔴 **CRITICAL** — {len(critical_buses)} bus(es) need immediate attention: "
             f"{', '.join([b['bus_id'] for b in critical_buses])}")
    
if high_buses:
    st.warning(f"🟠 **HIGH** — {len(high_buses)} bus(es) require review: "
               f"{', '.join([b['bus_id'] for b in high_buses])}")

if medium_buses:
    st.info(f"🟡 **MEDIUM** — {len(medium_buses)} bus(es) to monitor: "
            f"{', '.join([b['bus_id'] for b in medium_buses])}")

low_buses = [i for i in sorted_insights if i['severity'] == 'LOW']
if low_buses:
    st.success(f"🟢 **LOW** — {len(low_buses)} bus(es) operating normally: "
               f"{', '.join([b['bus_id'] for b in low_buses])}")

# Risk Score Chart
st.subheader("📊 Risk Score Comparison")
risk_df = pd.DataFrame([{
    'Bus': f"{i['bus_id']} ({i['route']})",
    'Risk Score': i['risk_score'],
    'Severity': i['severity']
} for i in sorted_insights])

fig = px.bar(
    risk_df, x='Bus', y='Risk Score', color='Severity',
    color_discrete_map=SEVERITY_COLORS,
    title="AI Risk Score by Bus"
)
fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="CRITICAL threshold")
fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="HIGH threshold")
fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="LOW threshold")
fig.update_layout(yaxis_range=[0, 105])
st.plotly_chart(fig, use_container_width=True)
