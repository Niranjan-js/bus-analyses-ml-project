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
    def render_sidebar_uploader():
        pass

from utils.analytics import (
    compute_kpis, compute_bus_utilization, compute_delay_analysis,
    compute_complaint_analysis, compute_route_performance, compute_student_analysis
)
from utils.theme import apply_theme, COLORS, SEVERITY_COLORS
from utils.reports import generate_csv_download, generate_executive_report_html
from ai.insights import generate_bus_insights, generate_system_summary
from ai.recommender import generate_recommendations

st.set_page_config(page_title="Super Admin Console", page_icon="👑", layout="wide")
apply_theme()
render_sidebar_uploader()

st.title("👑 Super Admin & Executive Management Console")
st.markdown("*High-level strategic intelligence, executive reports, fleet optimization, and multi-format report exports for college management.*")
st.divider()

data = load_data()
buses = data['buses']
students = data['students']
stops = data['stops']
usage = data['bus_usage']
complaints = data['complaints']

# Compute key metrics
kpis = compute_kpis(students, buses, stops, usage, complaints)
bus_util = compute_bus_utilization(usage, buses)
delay_df = compute_delay_analysis(usage, buses)
cat_dist, complaints_by_bus, comp_trend = compute_complaint_analysis(complaints, buses)
route_perf = compute_route_performance(usage, buses, complaints)

bus_insights = generate_bus_insights(bus_util, delay_df, complaints_by_bus)
system_summary = generate_system_summary(kpis, bus_insights)
recommendations = generate_recommendations(bus_insights, kpis)

# --- Role Selector ---
st.markdown("### 👤 Select Management View Mode")
role_mode = st.radio(
    "View Mode:",
    options=["👑 Super Admin (Full Control & Exports)", "📊 Transport Director (Executive Summary)", "🛠️ Operations Manager (Fleet & Drivers)"],
    horizontal=True
)

st.divider()

# --- Executive Top KPI Bar ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Fleet Size", f"{kpis['total_buses']} Buses", delta="Active")
col2.metric("Total Registered Users", f"{kpis['total_students']} Students")
col3.metric("Fleet Utilization Index", f"{kpis['avg_utilization']:.1f}%", delta="Target: 75-85%")
col4.metric("Delay Vulnerability Rate", f"{(kpis['delayed_trips']/kpis['total_trips'])*100:.1f}%")
col5.metric("Operational Health", kpis['system_health'])

st.divider()

# --- Section 1: Executive Summary & Health Radar ---
st.subheader("🏛️ Executive Strategic Overview")

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown(
        f"""
        <div style='background-color: #1B4F7210; border-left: 5px solid #1B4F72; padding: 20px; border-radius: 8px;'>
            <h3 style='margin-top:0; color:#1B4F72;'>AI Management Audit Summary</h3>
            <p><b>Overall Status:</b> <span style='font-size: 1.2em; font-weight: bold;'>{system_summary['health_status']}</span></p>
            <p>{system_summary['key_findings']}</p>
            <p><b>Top Strategic Focus:</b> Address capacity bottlenecks on routes operating near maximum threshold while reducing schedule variance.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("#### ⚡ Priority Management Action Checklist")
    for rec in recommendations[:4]:
        st.markdown(f"- **[{rec['priority']}] {rec['title']}** ({rec['urgency']} Urgency)")
        st.caption(f"Impact: {rec['expected_impact']} | Action: {rec['description']}")

with col_right:
    st.subheader("🎯 Fleet Efficiency Index")
    
    # Calculate fleet efficiency components
    util_score = min(kpis['avg_utilization'], 100)
    punctuality_score = max(0, 100 - ((kpis['delayed_trips'] / kpis['total_trips']) * 100))
    satisfaction_score = max(0, 100 - (kpis['total_complaints'] * 1.0))
    
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=(util_score * 0.4 + punctuality_score * 0.35 + satisfaction_score * 0.25),
        title={'text': "Composite Transport Score (0-100)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1B4F72"},
            'steps': [
                {'range': [0, 50], 'color': "#E74C3C"},
                {'range': [50, 75], 'color': "#F39C12"},
                {'range': [75, 100], 'color': "#27AE60"}
            ]
        }
    ))
    gauge_fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(gauge_fig, use_container_width=True)

st.divider()

# --- Section 2: Fleet Performance & Driver Matrix ---
st.subheader("🚌 Fleet & Driver Operations Audit")

tab1, tab2, tab3 = st.tabs(["🚍 Bus Performance & Risk Matrix", "👨‍✈️ Driver Performance", "🏢 Department Demand Index"])

with tab1:
    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("#### Bus Risk & Utilization Audit Table")
        bus_audit_df = bus_util.merge(delay_df[['bus_id', 'avg_delay', 'delayed_trips']], on='bus_id')
        bus_audit_df = bus_audit_df.merge(complaints_by_bus[['bus_id', 'count']], on='bus_id', how='left').fillna({'count': 0})
        bus_audit_df.rename(columns={'count': 'complaint_count', 'utilization_pct': 'utilization_%'}, inplace=True)
        bus_audit_df['utilization_%'] = bus_audit_df['utilization_%'].round(1)
        bus_audit_df['avg_delay'] = bus_audit_df['avg_delay'].round(1)
        
        st.dataframe(
            bus_audit_df[['bus_id', 'route', 'total_capacity', 'avg_students', 'utilization_%', 'category', 'avg_delay', 'complaint_count']],
            use_container_width=True,
            hide_index=True
        )
    
    with col_b:
        st.markdown("#### Risk Level Distribution")
        risk_counts = pd.Series([b['severity'] for b in bus_insights]).value_counts().reset_index()
        risk_counts.columns = ['severity', 'count']
        fig_risk = px.pie(
            risk_counts, names='severity', values='count',
            color='severity', color_discrete_map=SEVERITY_COLORS,
            hole=0.4, title="Buses by AI Risk Severity"
        )
        st.plotly_chart(fig_risk, use_container_width=True)

with tab2:
    st.markdown("#### Driver Performance Summary")
    driver_df = buses.merge(delay_df[['bus_id', 'avg_delay', 'delayed_trips']], on='bus_id')
    driver_df = driver_df.merge(complaints_by_bus[['bus_id', 'count']], on='bus_id', how='left').fillna({'count': 0})
    driver_df.rename(columns={'count': 'complaints_received'}, inplace=True)
    driver_df['avg_delay_min'] = driver_df['avg_delay'].round(1)
    
    st.dataframe(
        driver_df[['driver', 'bus_id', 'route', 'avg_delay_min', 'delayed_trips', 'complaints_received']],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown("#### Department Demand & Bus Assignment Matrix")
    dept_df, year_df, bus_assign = compute_student_analysis(students, buses)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_dept = px.bar(dept_df, x='department', y='count', color='department', title="Transport Users by Department")
        st.plotly_chart(fig_dept, use_container_width=True)
    with col_d2:
        fig_year = px.pie(year_df, names='year', values='count', title="Student Distribution by Academic Year", hole=0.3)
        st.plotly_chart(fig_year, use_container_width=True)

st.divider()

# --- Section 3: Interactive Capacity Re-Allocation Simulator ---
st.subheader("🛠️ Fleet Capacity Re-Allocation Simulator")
st.markdown("*Simulate transferring bus capacity or adding secondary buses to eliminate peak overcrowding.*")

sim_col1, sim_col2 = st.columns(2)
with sim_col1:
    target_bus = st.selectbox("Select Target Bus for Capacity Simulation", options=buses['bus_id'].tolist(), index=2)
    additional_seats = st.slider("Add Extra Seats / Secondary Vehicle Seats", min_value=0, max_value=40, value=15, step=5)

with sim_col2:
    bus_row = bus_util[bus_util['bus_id'] == target_bus].iloc[0]
    current_cap = bus_row['total_capacity']
    avg_st = bus_row['avg_students']
    curr_util = bus_row['utilization_pct']
    
    new_cap = current_cap + additional_seats
    new_util = (avg_st / new_cap) * 100
    
    st.markdown(f"**Current Status for {target_bus} ({bus_row['route']}):**")
    st.markdown(f"- Capacity: **{current_cap}** seats | Avg Boarded: **{avg_st:.1f}** | Utilization: **{curr_util:.1f}%** ({bus_row['category']})")
    st.markdown(f"**Simulated Status (+{additional_seats} seats):**")
    st.markdown(f"- New Capacity: **{new_cap}** seats | New Simulated Utilization: **{new_util:.1f}%**")
    
    if new_util <= 75:
        st.success("🟢 Simulation Result: Capacity bottleneck completely resolved! Utilization within safe limits.")
    elif new_util <= 85:
        st.info("🟡 Simulation Result: Acceptable utilization. Overcrowding risk reduced.")
    else:
        st.warning("🔴 Simulation Result: Still near capacity. Consider further capacity additions.")

st.divider()

# --- Section 4: One-Click Reports & Download Center ---
st.subheader("📥 Executive Download & Export Center")
st.markdown("*Download comprehensive CSV logs, analytical reports, and printable Executive Summaries.*")

d_col1, d_col2, d_col3, d_col4 = st.columns(4)

with d_col1:
    st.markdown("#### 📄 Executive Report")
    html_report = generate_executive_report_html(kpis, bus_insights, system_summary, recommendations)
    st.download_button(
        label="📥 Download Executive HTML/PDF Report",
        data=html_report,
        file_name="Executive_Transport_Management_Report.html",
        mime="text/html",
        use_container_width=True
    )

with d_col2:
    st.markdown("#### 🚌 Bus Risk Audit")
    bus_risk_export_df = pd.DataFrame([{
        'bus_id': b['bus_id'],
        'route': b['route'],
        'risk_score': b['risk_score'],
        'severity': b['severity'],
        'utilization_%': round(b['evidence']['utilization'], 1),
        'avg_delay_min': round(b['evidence']['avg_delay'], 1),
        'complaint_count': int(b['evidence']['complaints']),
        'recommendation': b['recommendation']
    } for b in bus_insights])
    generate_csv_download(bus_risk_export_df, "Bus_Risk_Audit_Report.csv", label="📥 Download Risk Audit CSV")

with d_col3:
    st.markdown("#### 📢 Complaints Log")
    generate_csv_download(complaints, "Complaints_Full_Audit.csv", label="📥 Download Complaints CSV")

with d_col4:
    st.markdown("#### 🛣️ Route Performance")
    generate_csv_download(route_perf, "Route_Performance_Report.csv", label="📥 Download Route Report CSV")

st.divider()
st.caption("👑 Super Admin Console • AI College Transport Analyzer • Final Version")
