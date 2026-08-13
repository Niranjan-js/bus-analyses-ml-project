import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from utils.data_loader import load_data
from utils.theme import apply_theme
from ai.predictor import predict_demand, get_capacity_alerts

st.set_page_config(page_title="Demand Prediction", page_icon="🔮", layout="wide")
apply_theme()

st.title("🔮 AI Demand Prediction")
st.markdown("*Random Forest model predicting next-day passenger demand based on historical usage patterns*")
st.divider()

data = load_data()

# Run prediction
with st.spinner("Training prediction model..."):
    predictions = predict_demand(data['bus_usage'], data['buses'])

if predictions is not None and not predictions.empty:
    # Merge with route info
    predictions = predictions.merge(
        data['buses'][['bus_id', 'route']], on='bus_id', how='left'
    )
    
    # KPI Row
    col1, col2, col3 = st.columns(3)
    avg_pred_util = predictions['utilization_forecast'].mean()
    critical_count = len(predictions[predictions['alert_level'] == 'Critical'])
    warning_count = len(predictions[predictions['alert_level'] == 'Warning'])
    
    col1.metric("Avg Predicted Utilization", f"{avg_pred_util:.1f}%")
    col2.metric("Critical Alerts", critical_count, delta=None)
    col3.metric("Warning Alerts", warning_count, delta=None)
    
    st.divider()
    
    # Predicted Demand vs Capacity Chart
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Predicted Demand vs Capacity")
        fig = go.Figure()
        
        colors = predictions['alert_level'].map({
            'Normal': '#27AE60', 'Warning': '#F39C12', 'Critical': '#E74C3C'
        }).tolist()
        
        fig.add_trace(go.Bar(
            x=predictions['bus_id'],
            y=predictions['predicted_passengers'],
            name='Predicted Passengers',
            marker_color=colors,
            text=predictions['predicted_passengers'],
            textposition='auto'
        ))
        
        fig.add_trace(go.Scatter(
            x=predictions['bus_id'],
            y=predictions['total_capacity'],
            name='Capacity',
            mode='markers+lines',
            marker=dict(size=12, symbol='diamond', color='#2C3E50'),
            line=dict(dash='dash', color='#2C3E50')
        ))
        
        fig.update_layout(
            title="Next-Day Demand Forecast",
            xaxis_title="Bus ID",
            yaxis_title="Passengers",
            barmode='group',
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Capacity Alerts")
        alerts = get_capacity_alerts(predictions)
        
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'CRITICAL':
                    st.error(f"🔴 **{alert['bus_id']}**: {alert['message']}")
                else:
                    st.warning(f"🟠 **{alert['bus_id']}**: {alert['message']}")
        else:
            st.success("✅ No capacity alerts. All buses within safe limits.")
        
        st.divider()
        
        # Legend
        st.markdown("""
        **Alert Levels:**
        - 🟢 **Normal**: < 85% utilization
        - 🟠 **Warning**: 85-100% utilization  
        - 🔴 **Critical**: > 100% utilization
        """)
    
    # Detailed Prediction Table
    st.subheader("📋 Detailed Predictions")
    display_df = predictions[['bus_id', 'route', 'predicted_passengers', 'total_capacity', 
                               'utilization_forecast', 'alert_level']].copy()
    display_df.columns = ['Bus ID', 'Route', 'Predicted Passengers', 'Capacity', 
                           'Predicted Utilization %', 'Alert Level']
    display_df['Predicted Utilization %'] = display_df['Predicted Utilization %'].round(1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Per-bus prediction cards
    st.subheader("🚌 Per-Bus Forecast")
    cols = st.columns(3)
    for i, (_, row) in enumerate(predictions.iterrows()):
        with cols[i % 3]:
            alert_emoji = {'Normal': '🟢', 'Warning': '🟠', 'Critical': '🔴'}.get(row['alert_level'], '🟢')
            overflow = row['predicted_passengers'] - row['total_capacity']
            
            st.markdown(f"""
            <div style='padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px;'>
                <h4>{alert_emoji} {row['bus_id']} ({row['route']})</h4>
                <p><b>Predicted:</b> {int(row['predicted_passengers'])} students</p>
                <p><b>Capacity:</b> {int(row['total_capacity'])} seats</p>
                <p><b>Utilization:</b> {row['utilization_forecast']:.1f}%</p>
                {'<p style="color: red;"><b>⚠️ Overflow: ' + str(int(overflow)) + ' students</b></p>' if overflow > 0 else '<p style="color: green;"><b>✅ Within capacity</b></p>'}
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.info("**Model Info:** Random Forest Regressor with features: day_of_week, week_number, bus_id, 3-day rolling avg, 5-day rolling avg. Trained on 22 days of historical data.")
    
else:
    st.warning("⚠️ Insufficient data for prediction. Need at least 10 records per bus.")
