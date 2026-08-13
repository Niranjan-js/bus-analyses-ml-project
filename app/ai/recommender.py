def generate_recommendations(bus_insights, kpis):
    """Generate prioritized management recommendations."""
    recommendations = []
    priority_counter = 1
    
    for bus in sorted(bus_insights, key=lambda x: x['risk_score'], reverse=True):
        if "High utilization" in bus['problems'] or "Over-capacity" in bus['problems']:
            recommendations.append({
                'priority': priority_counter,
                'category': 'Capacity Management',
                'title': f"Address Overcrowding on Route {bus['route']}",
                'description': f"Bus {bus['bus_id']} is experiencing high utilization ({bus['evidence']['utilization']:.1f}%).",
                'affected_buses': [bus['bus_id']],
                'expected_impact': "Increase student comfort and safety",
                'urgency': bus['severity']
            })
            priority_counter += 1
            
        if "Frequent delays" in bus['problems']:
            recommendations.append({
                'priority': priority_counter,
                'category': 'Schedule Optimization',
                'title': f"Review Schedule for Route {bus['route']}",
                'description': f"Bus {bus['bus_id']} has an average delay of {bus['evidence']['avg_delay']:.1f} minutes.",
                'affected_buses': [bus['bus_id']],
                'expected_impact': "Improve punctuality",
                'urgency': 'HIGH' if bus['evidence']['avg_delay'] > 15 else 'MEDIUM'
            })
            priority_counter += 1
            
        if "High complaint volume" in bus['problems']:
            recommendations.append({
                'priority': priority_counter,
                'category': 'Student Experience',
                'title': f"Investigate Complaints on {bus['bus_id']}",
                'description': f"Bus {bus['bus_id']} has received {bus['evidence']['complaints']} complaints, significantly above average.",
                'affected_buses': [bus['bus_id']],
                'expected_impact': "Improve student satisfaction",
                'urgency': bus['severity']
            })
            priority_counter += 1
            
        if "Underutilized" in bus['problems']:
            recommendations.append({
                'priority': priority_counter,
                'category': 'Route Optimization',
                'title': f"Optimize Underutilized Route {bus['route']}",
                'description': f"Bus {bus['bus_id']} is running at low capacity ({bus['evidence']['utilization']:.1f}%). Consider consolidating.",
                'affected_buses': [bus['bus_id']],
                'expected_impact': "Reduce operational costs",
                'urgency': 'LOW'
            })
            priority_counter += 1
            
    return recommendations
