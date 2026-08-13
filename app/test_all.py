import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test data loading
from utils.data_loader import load_data
data = load_data()
print('=== Data Loaded ===')
for k, v in data.items():
    print(f'{k}: {v.shape}')

# Test analytics
from utils.analytics import (compute_kpis, compute_bus_utilization, 
    compute_delay_analysis, compute_complaint_analysis,
    compute_student_analysis, compute_stop_analysis, compute_daily_trends)

kpis = compute_kpis(data['students'], data['buses'], data['stops'], data['bus_usage'], data['complaints'])
print('\n=== KPIs ===')
for k, v in kpis.items():
    print(f'  {k}: {v}')

bus_util = compute_bus_utilization(data['bus_usage'], data['buses'])
print('\n=== Bus Utilization ===')
print(bus_util[['bus_id', 'route', 'total_capacity', 'avg_students', 'utilization_pct', 'category']].to_string(index=False))

delay = compute_delay_analysis(data['bus_usage'], data['buses'])
print('\n=== Delay Analysis ===')
print(delay[['bus_id', 'route', 'total_trips', 'delayed_trips', 'avg_delay', 'severity']].to_string(index=False))

cat, by_bus, trend = compute_complaint_analysis(data['complaints'], data['buses'])
print('\n=== Complaint Categories ===')
print(cat.to_string(index=False))

dept, year, bus_assign = compute_student_analysis(data['students'], data['buses'])
print('\n=== Department Usage ===')
print(dept.to_string(index=False))

stop_usage = compute_stop_analysis(data['students'], data['stops'])
print('\n=== Stop Usage (Top 5) ===')
print(stop_usage.sort_values('student_count', ascending=False).head().to_string(index=False))

# Test AI insights
from ai.insights import generate_bus_insights, generate_system_summary
insights = generate_bus_insights(bus_util, delay, by_bus)
print('\n=== AI Insights ===')
for i in sorted(insights, key=lambda x: x['risk_score'], reverse=True):
    print(f"  Bus {i['bus_id']}: Risk={i['risk_score']}, Severity={i['severity']}, Problems={i['problems']}")

summary = generate_system_summary(kpis, insights)
print(f"\n  System Health: {summary['health_status']}")
print(f"  Key Findings: {summary['key_findings']}")

# Test recommender
from ai.recommender import generate_recommendations
recs = generate_recommendations(insights, kpis)
print('\n=== AI Recommendations ===')
for r in recs[:3]:
    print(f"  [{r['priority']}] {r['title']} - {r['urgency']}")

# Test predictor
from ai.predictor import predict_demand, get_capacity_alerts
preds = predict_demand(data['bus_usage'], data['buses'])
print('\n=== Predictions ===')
if not preds.empty:
    print(preds[['bus_id', 'predicted_passengers', 'total_capacity', 'utilization_forecast', 'alert_level']].to_string(index=False))
    alerts = get_capacity_alerts(preds)
    print(f'  Capacity alerts: {len(alerts)}')
else:
    print('  No predictions generated')

# Test chat
from ai.chat import ask_transport_ai
analytics_results = {'bus_utilization': bus_util, 'delay_analysis': delay, 'kpis': kpis}

test_questions = [
    'Which bus is most crowded?',
    'Which route has the most delays?',
    'What are the top complaint categories?',
    'What should management do?',
    'Give me a system summary'
]

print('\n=== Chat Tests ===')
for q in test_questions:
    result = ask_transport_ai(q, data, analytics_results)
    print(f"\n  Q: {q}")
    print(f"  A: {result['answer']}")
    if result['evidence']:
        print(f"  Evidence: {result['evidence'][:100]}...")

print('\n✅ ALL TESTS PASSED!')
