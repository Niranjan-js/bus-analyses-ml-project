import pandas as pd
import numpy as np

def compute_bus_utilization(bus_usage_df, buses_df):
    """Returns DataFrame with: bus_id, route, total_capacity, avg_students, utilization_pct, category"""
    # Merge to get capacity
    merged = bus_usage_df.merge(buses_df[['bus_id', 'route', 'total_capacity']], on='bus_id', how='left')
    
    # Calculate avg passengers per bus
    avg_passengers = merged.groupby(['bus_id', 'route', 'total_capacity'])['students_boarded'].mean().reset_index()
    avg_passengers = avg_passengers.rename(columns={'students_boarded': 'avg_students'})
    
    # Calculate utilization
    avg_passengers['utilization_pct'] = (avg_passengers['avg_students'] / avg_passengers['total_capacity']) * 100
    
    def categorize_utilization(pct):
        if pct < 40: return 'Underutilized'
        elif pct <= 70: return 'Normal'
        elif pct <= 85: return 'High'
        elif pct <= 100: return 'Critical'
        else: return 'Over-capacity'
        
    avg_passengers['category'] = avg_passengers['utilization_pct'].apply(categorize_utilization)
    return avg_passengers

def compute_delay_analysis(bus_usage_df, buses_df):
    """Returns DataFrame with: bus_id, route, total_trips, delayed_trips, delay_rate, avg_delay, max_delay, severity"""
    merged = bus_usage_df.merge(buses_df[['bus_id', 'route']], on='bus_id', how='left')
    
    delay_stats = merged.groupby(['bus_id', 'route']).agg(
        total_trips=('date', 'count'),
        delayed_trips=('delay_minutes', lambda x: (x > 0).sum()),
        avg_delay=('delay_minutes', 'mean'),
        max_delay=('delay_minutes', 'max')
    ).reset_index()
    
    delay_stats['delay_rate'] = (delay_stats['delayed_trips'] / delay_stats['total_trips']) * 100
    
    def get_severity(avg_delay):
        if avg_delay == 0: return 'LOW'
        elif avg_delay <= 5: return 'LOW'
        elif avg_delay <= 10: return 'MEDIUM'
        elif avg_delay <= 15: return 'HIGH'
        else: return 'CRITICAL'
        
    delay_stats['severity'] = delay_stats['avg_delay'].apply(get_severity)
    return delay_stats

def compute_route_performance(bus_usage_df, buses_df, complaints_df):
    """Returns DataFrame with: route, bus_id, total_trips, avg_passengers, avg_utilization, avg_delay, complaint_count, health_status"""
    util_df = compute_bus_utilization(bus_usage_df, buses_df)
    delay_df = compute_delay_analysis(bus_usage_df, buses_df)
    
    complaint_counts = complaints_df.groupby('bus_id').size().reset_index(name='complaint_count')
    
    route_perf = util_df.merge(delay_df[['bus_id', 'total_trips', 'avg_delay']], on='bus_id')
    route_perf = route_perf.merge(complaint_counts, on='bus_id', how='left').fillna({'complaint_count': 0})
    route_perf.rename(columns={'utilization_pct': 'avg_utilization'}, inplace=True)
    
    def get_health_status(row):
        score = 0
        if row['avg_utilization'] > 85: score += 2
        elif row['avg_utilization'] < 40: score += 1
        
        if row['avg_delay'] > 10: score += 2
        elif row['avg_delay'] > 5: score += 1
        
        if row['complaint_count'] > 10: score += 2
        elif row['complaint_count'] > 5: score += 1
        
        if score >= 4: return 'Poor'
        elif score >= 2: return 'Fair'
        else: return 'Good'
        
    route_perf['health_status'] = route_perf.apply(get_health_status, axis=1)
    return route_perf

def compute_complaint_analysis(complaints_df, buses_df):
    """Returns: category_dist, complaints_by_bus, complaint_trend"""
    category_dist = complaints_df.groupby('category').size().reset_index(name='count')
    category_dist['pct'] = (category_dist['count'] / category_dist['count'].sum()) * 100
    
    merged = complaints_df.merge(buses_df[['bus_id', 'route']], on='bus_id', how='left')
    complaints_by_bus = merged.groupby(['bus_id', 'route']).size().reset_index(name='count')
    
    complaint_trend = complaints_df.groupby('date').size().reset_index(name='count')
    
    return category_dist, complaints_by_bus, complaint_trend

def compute_student_analysis(students_df, buses_df):
    """Returns: dept_usage, year_dist, bus_assignment"""
    dept_usage = students_df.groupby('department').size().reset_index(name='count')
    dept_usage['pct'] = (dept_usage['count'] / dept_usage['count'].sum()) * 100
    
    year_dist = students_df.groupby('year').size().reset_index(name='count')
    
    bus_assignment = students_df.groupby('bus_id').size().reset_index(name='count')
    
    return dept_usage, year_dist, bus_assignment

def compute_stop_analysis(students_df, stops_df):
    """Returns: stop_usage"""
    stop_counts = students_df.groupby('stop_id').size().reset_index(name='student_count')
    stop_usage = stops_df.merge(stop_counts, on='stop_id', how='left').fillna({'student_count': 0})
    stop_usage['rank'] = stop_usage['student_count'].rank(ascending=False, method='min')
    return stop_usage

def compute_kpis(students_df, buses_df, stops_df, bus_usage_df, complaints_df):
    """Returns dict with all KPI values"""
    total_students = len(students_df)
    total_buses = len(buses_df)
    total_stops = len(stops_df)
    
    merged_usage = bus_usage_df.merge(buses_df[['bus_id', 'total_capacity']], on='bus_id')
    avg_utilization = (merged_usage['students_boarded'].sum() / merged_usage['total_capacity'].sum()) * 100
    
    delayed_trips = (bus_usage_df['delay_minutes'] > 0).sum()
    total_complaints = len(complaints_df)
    
    # Determine system health
    if avg_utilization > 90 or delayed_trips > len(bus_usage_df) * 0.8:
        system_health = 'CRITICAL'
    elif avg_utilization > 75 or delayed_trips > len(bus_usage_df) * 0.5:
        system_health = 'ATTENTION'
    else:
        system_health = 'HEALTHY'
    
    return {
        'total_students': total_students,
        'total_buses': total_buses,
        'total_stops': total_stops,
        'total_trips': len(bus_usage_df),
        'avg_utilization': avg_utilization,
        'delayed_trips': int(delayed_trips),
        'total_complaints': total_complaints,
        'avg_delay': bus_usage_df['delay_minutes'].mean(),
        'max_delay': bus_usage_df['delay_minutes'].max(),
        'system_health': system_health
    }

def compute_daily_trends(bus_usage_df, buses_df):
    """Returns DataFrame with daily utilization and delay trends."""
    merged = bus_usage_df.merge(buses_df[['bus_id', 'total_capacity']], on='bus_id')
    daily = merged.groupby('date').agg(
        total_boarded=('students_boarded', 'sum'),
        total_capacity=('total_capacity', 'sum'),
        avg_delay=('delay_minutes', 'mean')
    ).reset_index()
    daily['avg_utilization'] = (daily['total_boarded'] / daily['total_capacity']) * 100
    return daily
