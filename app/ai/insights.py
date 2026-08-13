def get_severity(risk_score):
    """0-30=LOW, 31-60=MEDIUM, 61-80=HIGH, 81-100=CRITICAL"""
    if risk_score <= 30: return 'LOW'
    elif risk_score <= 60: return 'MEDIUM'
    elif risk_score <= 80: return 'HIGH'
    else: return 'CRITICAL'

def generate_bus_insights(bus_util_df, delay_df, complaints_by_bus_df):
    """Generate AI insights for each bus."""
    insights = []
    
    # Merge datasets to get a complete view
    merged = bus_util_df.merge(delay_df[['bus_id', 'avg_delay', 'delay_rate']], on='bus_id', how='left')
    if not complaints_by_bus_df.empty:
        merged = merged.merge(complaints_by_bus_df[['bus_id', 'count']], on='bus_id', how='left').fillna({'count': 0})
        merged.rename(columns={'count': 'complaint_count'}, inplace=True)
    else:
        merged['complaint_count'] = 0
        
    avg_complaints = merged['complaint_count'].mean() if len(merged) > 0 else 0
        
    for _, row in merged.iterrows():
        bus_id = row['bus_id']
        route = row['route']
        util = row['utilization_pct']
        avg_delay = row.get('avg_delay', 0)
        complaints = row.get('complaint_count', 0)
        
        # Utilization risk (40% weight)
        if util < 40: u_risk = 10
        elif util <= 70: u_risk = 30
        elif util <= 85: u_risk = 60
        elif util <= 100: u_risk = 85
        else: u_risk = 100
        
        # Delay risk (30% weight)
        if avg_delay == 0: d_risk = 0
        elif avg_delay <= 5: d_risk = 20
        elif avg_delay <= 10: d_risk = 50
        elif avg_delay <= 15: d_risk = 75
        else: d_risk = 100
            
        # Complaint risk (30% weight)
        if avg_complaints > 0:
            c_ratio = complaints / avg_complaints
            if c_ratio <= 0.5: c_risk = 10
            elif c_ratio <= 1.0: c_risk = 30
            elif c_ratio <= 1.5: c_risk = 60
            elif c_ratio <= 2.0: c_risk = 80
            else: c_risk = 100
        else:
            c_risk = 0
            
        risk_score = (0.4 * u_risk) + (0.3 * d_risk) + (0.3 * c_risk)
        
        problems = []
        if util > 85: problems.append("High utilization")
        elif util < 40: problems.append("Underutilized")
        if avg_delay > 10: problems.append("Frequent delays")
        if complaints > avg_complaints * 1.5: problems.append("High complaint volume")
            
        recommendation = "Maintain current operations."
        expected_impact = "Stable performance."
        if "High utilization" in problems:
            recommendation = "Consider assigning a larger bus or adding a secondary route."
            expected_impact = "Reduce crowding and improve student comfort."
        elif "Frequent delays" in problems:
            recommendation = "Review route schedule and identify traffic bottlenecks."
            expected_impact = "Improve on-time performance."
            
        insights.append({
            'bus_id': bus_id,
            'route': route,
            'severity': get_severity(risk_score),
            'risk_score': round(risk_score, 1),
            'problems': problems,
            'evidence': {'utilization': util, 'avg_delay': avg_delay, 'complaints': complaints},
            'recommendation': recommendation,
            'expected_impact': expected_impact
        })
        
    return insights

def generate_system_summary(kpis, bus_insights):
    """Generate overall system health summary."""
    high_risk_buses = [b for b in bus_insights if b['severity'] in ['HIGH', 'CRITICAL']]
    
    health_status = 'Good'
    if len(high_risk_buses) > 2 or kpis['avg_utilization'] > 90:
        health_status = 'Critical'
    elif len(high_risk_buses) > 0 or kpis['avg_utilization'] > 80:
        health_status = 'Fair'
        
    key_findings = f"System operating at {kpis['avg_utilization']:.1f}% average utilization. {kpis['delayed_trips']} delayed trips recorded. {kpis['total_complaints']} total complaints."
    top_risks = [f"Bus {b['bus_id']} ({b['route']}) - {b['severity']} Risk" for b in high_risk_buses]
    
    priority_actions = []
    if high_risk_buses:
        priority_actions.append(f"Review operations for high risk buses: {', '.join([b['bus_id'] for b in high_risk_buses])}")
    if kpis['avg_utilization'] > 85:
        priority_actions.append("Consider fleet expansion or route optimization to handle high overall capacity.")
        
    return {
        'health_status': health_status,
        'key_findings': key_findings,
        'top_risks': top_risks,
        'priority_actions': priority_actions
    }
