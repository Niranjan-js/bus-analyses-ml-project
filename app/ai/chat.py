import re
import pandas as pd


def ask_transport_ai(question, data, analytics_results):
    """Natural language Q&A for transport data.
    
    Handles 20+ question patterns using keyword matching and data lookup.
    All answers are generated from actual data, not hallucinated.
    """
    q_lower = question.lower().strip()
    
    # Extract data components
    buses_df = data.get('buses')
    students_df = data.get('students')
    stops_df = data.get('stops')
    bus_usage_df = data.get('bus_usage')
    complaints_df = data.get('complaints')
    bus_util = analytics_results.get('bus_utilization')
    delay_df = analytics_results.get('delay_analysis')
    kpis = analytics_results.get('kpis', {})
    
    answer = "I'm not sure how to answer that based on the current data. Try asking about bus utilization, delays, complaints, departments, or stops."
    evidence = None
    recommendation = None
    
    # --- 1. Most crowded / highest utilization ---
    if re.search(r'most (crowded|utiliz|packed|full|busy)', q_lower) or \
       re.search(r'highest (utiliz|capacity|usage)', q_lower) or \
       re.search(r'overcrowded', q_lower):
        if bus_util is not None and not bus_util.empty:
            top = bus_util.sort_values('utilization_pct', ascending=False).iloc[0]
            answer = f"Bus {top['bus_id']} on {top['route']} is the most crowded bus."
            evidence = (f"Average utilization: {top['utilization_pct']:.1f}% "
                       f"({top['avg_students']:.0f} students / {int(top['total_capacity'])} capacity). "
                       f"Category: {top['category']}.")
            if top['utilization_pct'] > 85:
                recommendation = "This bus is critically loaded. Consider adding a second bus on this route during peak hours, or reassigning some students to less crowded routes."
            else:
                recommendation = "Monitor this bus closely during peak periods."
    
    # --- 2. Most delayed ---
    elif re.search(r'(most|highest|top|worst).*(delay|late)', q_lower) or \
         re.search(r'delay.*(most|highest|top|worst)', q_lower):
        if delay_df is not None and not delay_df.empty:
            top = delay_df.sort_values('avg_delay', ascending=False).iloc[0]
            answer = f"Bus {top['bus_id']} on {top['route']} has the highest average delay."
            evidence = (f"Average delay: {top['avg_delay']:.1f} minutes. "
                       f"Delayed on {int(top['delayed_trips'])}/{int(top['total_trips'])} trips "
                       f"({top['delay_rate']:.1f}%). Max delay: {int(top['max_delay'])} min.")
            recommendation = "Review the route schedule, identify traffic bottlenecks, or consider an earlier departure time."
    
    # --- 3. Top complaints / most common complaint ---
    elif re.search(r'(top|most|common|main|major).*(complaint|issue|problem)', q_lower) or \
         re.search(r'complaint.*(top|most|common|main|category)', q_lower):
        if complaints_df is not None and not complaints_df.empty:
            cats = complaints_df['category'].value_counts().reset_index()
            cats.columns = ['category', 'count']
            total = len(complaints_df)
            top3 = cats.head(3)
            answer = f"The most common complaint is '{top3.iloc[0]['category']}' with {int(top3.iloc[0]['count'])} complaints ({top3.iloc[0]['count']/total*100:.0f}%)."
            evidence = "Top 3 categories:\n" + "\n".join(
                [f"  • {row['category']}: {int(row['count'])} ({row['count']/total*100:.0f}%)" 
                 for _, row in top3.iterrows()]
            )
            recommendation = f"Prioritize resolving '{top3.iloc[0]['category']}' issues to address the largest volume of student complaints."
    
    # --- 4. Underutilized ---
    elif re.search(r'(underutiliz|least (used|utiliz)|empty|lowest utiliz)', q_lower):
        if bus_util is not None and not bus_util.empty:
            bottom = bus_util.sort_values('utilization_pct', ascending=True).iloc[0]
            answer = f"Bus {bottom['bus_id']} on {bottom['route']} is the most underutilized."
            evidence = (f"Average utilization: {bottom['utilization_pct']:.1f}% "
                       f"({bottom['avg_students']:.0f} students / {int(bottom['total_capacity'])} capacity).")
            recommendation = "Consider using a smaller vehicle for this route, or consolidate with another low-usage route to improve efficiency."
    
    # --- 5. Department usage ---
    elif re.search(r'department', q_lower):
        if students_df is not None and not students_df.empty:
            dept_counts = students_df['department'].value_counts()
            top_dept = dept_counts.index[0]
            total = len(students_df)
            answer = f"The {top_dept} department has the most transport users with {dept_counts.iloc[0]} students."
            evidence = "Department breakdown:\n" + "\n".join(
                [f"  • {dept}: {count} students ({count/total*100:.0f}%)" 
                 for dept, count in dept_counts.items()]
            )
            recommendation = "Ensure routes serving areas with high department concentration have adequate capacity."
    
    # --- 6. Stop with most students ---
    elif re.search(r'stop', q_lower) and re.search(r'(most|busiest|highest|popular)', q_lower):
        if students_df is not None and not students_df.empty:
            stop_counts = students_df['stop_id'].value_counts()
            top_stop = stop_counts.index[0]
            answer = f"Stop {top_stop} has the most students with {stop_counts.iloc[0]} students boarding there."
            if stops_df is not None:
                stop_info = stops_df[stops_df['stop_id'] == top_stop]
                if not stop_info.empty:
                    evidence = f"Stop: {stop_info.iloc[0]['stop_name']}, Area: {stop_info.iloc[0]['area']}, Distance: {stop_info.iloc[0]['distance_km']} km"
    
    # --- 7. Specific bus inquiry (B01-B06) ---
    elif re.search(r'b0[1-6]', q_lower):
        bus_match = re.search(r'(b0[1-6])', q_lower).group(1).upper()
        student_count = len(students_df[students_df['bus_id'] == bus_match]) if students_df is not None else 0
        
        parts = [f"Bus {bus_match} Analysis:"]
        
        if buses_df is not None:
            bus_info = buses_df[buses_df['bus_id'] == bus_match]
            if not bus_info.empty:
                parts.append(f"Route: {bus_info.iloc[0]['route']}, Capacity: {int(bus_info.iloc[0]['total_capacity'])}")
        
        parts.append(f"Assigned students: {student_count}")
        
        evidence_parts = []
        if bus_util is not None and not bus_util.empty:
            util_info = bus_util[bus_util['bus_id'] == bus_match]
            if not util_info.empty:
                evidence_parts.append(f"Utilization: {util_info.iloc[0]['utilization_pct']:.1f}% ({util_info.iloc[0]['category']})")
        
        if delay_df is not None and not delay_df.empty:
            delay_info = delay_df[delay_df['bus_id'] == bus_match]
            if not delay_info.empty:
                evidence_parts.append(f"Avg delay: {delay_info.iloc[0]['avg_delay']:.1f} min, Delay rate: {delay_info.iloc[0]['delay_rate']:.1f}%")
        
        if complaints_df is not None and not complaints_df.empty:
            comp_count = len(complaints_df[complaints_df['bus_id'] == bus_match])
            evidence_parts.append(f"Complaints: {comp_count}")
        
        answer = " | ".join(parts)
        if evidence_parts:
            evidence = " | ".join(evidence_parts)
        
        # Check if it's a "why high risk" question
        if re.search(r'(risk|problem|issue|attention|concern|why)', q_lower):
            problems = []
            if bus_util is not None:
                u = bus_util[bus_util['bus_id'] == bus_match]
                if not u.empty and u.iloc[0]['utilization_pct'] > 85:
                    problems.append(f"high utilization ({u.iloc[0]['utilization_pct']:.1f}%)")
            if delay_df is not None:
                d = delay_df[delay_df['bus_id'] == bus_match]
                if not d.empty and d.iloc[0]['avg_delay'] > 10:
                    problems.append(f"frequent delays (avg {d.iloc[0]['avg_delay']:.1f} min)")
            if complaints_df is not None:
                cc = len(complaints_df[complaints_df['bus_id'] == bus_match])
                avg_cc = len(complaints_df) / len(buses_df) if buses_df is not None else 15
                if cc > avg_cc * 1.3:
                    problems.append(f"above-average complaints ({cc})")
            
            if problems:
                recommendation = f"Bus {bus_match} needs attention due to: {', '.join(problems)}. Consider reviewing the route schedule and capacity allocation."
            else:
                recommendation = f"Bus {bus_match} is operating within acceptable parameters."
    
    # --- 8. What should management do ---
    elif re.search(r'management|should|action|fix|improve|recommend', q_lower):
        if bus_util is not None and delay_df is not None:
            critical = bus_util[bus_util['utilization_pct'] > 85]
            underutil = bus_util[bus_util['utilization_pct'] < 40]
            high_delay = delay_df[delay_df['avg_delay'] > 10]
            
            actions = []
            if not critical.empty:
                buses_str = ", ".join(critical['bus_id'].tolist())
                actions.append(f"1. **Address overcrowding**: Buses {buses_str} are near/over capacity. Add capacity or redistribute students.")
            if not high_delay.empty:
                buses_str = ", ".join(high_delay['bus_id'].tolist())
                actions.append(f"2. **Reduce delays**: Buses {buses_str} have high average delays. Review route timing and traffic patterns.")
            if not underutil.empty:
                buses_str = ", ".join(underutil['bus_id'].tolist())
                actions.append(f"3. **Optimize underutilized routes**: Buses {buses_str} have low usage. Consider smaller vehicles or route consolidation.")
            if complaints_df is not None:
                top_cat = complaints_df['category'].value_counts().index[0]
                actions.append(f"4. **Address '{top_cat}' complaints**: This is the most common complaint category. Investigate root causes.")
            
            answer = "Based on the data analysis, here are the recommended management actions:"
            evidence = "\n".join(actions) if actions else "No critical issues detected."
            recommendation = "Start with the highest-priority items first: overcrowding and delays directly impact student safety and satisfaction."
    
    # --- 9. Summary / Overall ---
    elif re.search(r'summary|overall|health|overview|status', q_lower):
        total_students = kpis.get('total_students', len(students_df))
        total_buses = kpis.get('total_buses', len(buses_df))
        avg_util = kpis.get('avg_utilization', 0)
        delayed = kpis.get('delayed_trips', 0)
        total_comp = kpis.get('total_complaints', len(complaints_df))
        
        answer = f"Transport System Summary: {total_students} students across {total_buses} buses."
        evidence = (f"Average utilization: {avg_util:.1f}% | "
                   f"Delayed trips: {delayed} | "
                   f"Total complaints: {total_comp}")
        
        if avg_util > 85:
            recommendation = "System is under stress. Consider fleet expansion."
        elif avg_util < 50:
            recommendation = "System has excess capacity. Consider optimization."
        else:
            recommendation = "System is operating within normal parameters. Monitor high-utilization buses."
    
    # --- 10. Complaint by specific bus ---
    elif re.search(r'complaint', q_lower) and re.search(r'b0[1-6]', q_lower):
        bus_match = re.search(r'(b0[1-6])', q_lower).group(1).upper()
        if complaints_df is not None:
            bus_comps = complaints_df[complaints_df['bus_id'] == bus_match]
            if not bus_comps.empty:
                cats = bus_comps['category'].value_counts()
                answer = f"Bus {bus_match} has {len(bus_comps)} complaints."
                evidence = "Breakdown:\n" + "\n".join(
                    [f"  • {cat}: {count}" for cat, count in cats.items()]
                )
                recommendation = f"The main complaint for {bus_match} is '{cats.index[0]}'. Investigate and address this issue."
    
    # --- 11. How many total trips ---
    elif re.search(r'(total|how many).*(trip|ride)', q_lower):
        if bus_usage_df is not None:
            total_trips = len(bus_usage_df)
            answer = f"There are {total_trips} total bus trips recorded in the dataset."
            evidence = f"Covering {bus_usage_df['date'].nunique()} working days across {bus_usage_df['bus_id'].nunique()} buses."
    
    # --- 12. Capacity ---
    elif re.search(r'capacity', q_lower):
        if buses_df is not None:
            total_cap = buses_df['total_capacity'].sum()
            answer = f"The total fleet capacity is {int(total_cap)} students across {len(buses_df)} buses."
            evidence = "Per bus:\n" + "\n".join(
                [f"  • {row['bus_id']} ({row['route']}): {int(row['total_capacity'])} seats" 
                 for _, row in buses_df.iterrows()]
            )
    
    # --- 13. Route specific ---
    elif re.search(r'route', q_lower) and re.search(r'[a-f]', q_lower):
        route_match = re.search(r'route[-\s]?([a-f])', q_lower)
        if route_match:
            route_letter = route_match.group(1).upper()
            route_name = f"Route-{route_letter}"
            if buses_df is not None:
                bus_on_route = buses_df[buses_df['route'] == route_name]
                if not bus_on_route.empty:
                    bus_id = bus_on_route.iloc[0]['bus_id']
                    answer = f"{route_name} is served by Bus {bus_id} (Capacity: {int(bus_on_route.iloc[0]['total_capacity'])})."
                    if bus_util is not None:
                        u = bus_util[bus_util['bus_id'] == bus_id]
                        if not u.empty:
                            evidence = f"Utilization: {u.iloc[0]['utilization_pct']:.1f}% ({u.iloc[0]['category']})"
    
    # --- 14. Year/academic year ---
    elif re.search(r'year|academic', q_lower):
        if students_df is not None:
            year_counts = students_df['year'].value_counts().sort_index()
            answer = "Student distribution by academic year:"
            evidence = "\n".join(
                [f"  • Year {int(year)}: {count} students" for year, count in year_counts.items()]
            )
    
    # --- 15. Distance ---
    elif re.search(r'distance|far|closest|nearest', q_lower):
        if stops_df is not None:
            farthest = stops_df.sort_values('distance_km', ascending=False).iloc[0]
            closest = stops_df.sort_values('distance_km', ascending=True).iloc[0]
            answer = f"The farthest stop is {farthest['stop_name']} ({farthest['distance_km']} km) and the closest is {closest['stop_name']} ({closest['distance_km']} km)."
            evidence = f"Distance range: {closest['distance_km']} km to {farthest['distance_km']} km."
    
    return {
        'answer': answer,
        'evidence': evidence,
        'recommendation': recommendation
    }
