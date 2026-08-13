import io
import pandas as pd
import streamlit as st

def generate_csv_download(df: pd.DataFrame, filename: str, label: str = "📥 Download CSV"):
    """Generates a Streamlit download button for a DataFrame as CSV."""
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime='text/csv',
        use_container_width=True
    )

def generate_executive_report_html(kpis: dict, bus_insights: list, system_summary: dict, recommendations: list) -> str:
    """Generates a beautiful, printable HTML Executive Management Summary Report."""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI College Transport Analyzer — Executive Management Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #2C3E50; background: #F8F9FA; }}
            .header {{ text-align: center; border-bottom: 3px solid #1B4F72; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #1B4F72; margin: 0; font-size: 28px; }}
            .header p {{ color: #5D6D7E; margin-top: 5px; font-size: 14px; }}
            .kpi-container {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .kpi-card {{ background: #FFFFFF; border-radius: 8px; padding: 15px; width: 18%; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #1B4F72; }}
            .kpi-card h3 {{ margin: 0; color: #7F8C8D; font-size: 12px; text-transform: uppercase; }}
            .kpi-card p {{ margin: 10px 0 0 0; color: #2C3E50; font-size: 22px; font-weight: bold; }}
            .section {{ background: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section h2 {{ color: #1B4F72; border-bottom: 2px solid #EAECEE; padding-bottom: 10px; margin-top: 0; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #BDC3C7; padding: 10px; text-align: left; font-size: 13px; }}
            th {{ background-color: #1B4F72; color: white; }}
            tr:nth-child(even) {{ background-color: #F2F4F4; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; color: white; display: inline-block; }}
            .badge-low {{ background-color: #27AE60; }}
            .badge-medium {{ background-color: #F39C12; }}
            .badge-high {{ background-color: #E74C3C; }}
            .badge-critical {{ background-color: #8E44AD; }}
            .footer {{ text-align: center; font-size: 12px; color: #95A5A6; margin-top: 40px; border-top: 1px solid #BDC3C7; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚌 AI College Transport Analyzer</h1>
            <p>Executive Super Admin Report & Operations Audit</p>
        </div>

        <div class="kpi-container">
            <div class="kpi-card">
                <h3>Total Students</h3>
                <p>{kpis.get('total_students', 0)}</p>
            </div>
            <div class="kpi-card">
                <h3>Active Fleet</h3>
                <p>{kpis.get('total_buses', 0)} Buses</p>
            </div>
            <div class="kpi-card">
                <h3>Avg Utilization</h3>
                <p>{kpis.get('avg_utilization', 0):.1f}%</p>
            </div>
            <div class="kpi-card">
                <h3>Delayed Trips</h3>
                <p>{kpis.get('delayed_trips', 0)}</p>
            </div>
            <div class="kpi-card">
                <h3>System Health</h3>
                <p>{kpis.get('system_health', 'N/A')}</p>
            </div>
        </div>

        <div class="section">
            <h2>🧠 System Health Summary</h2>
            <p><strong>Status:</strong> {system_summary.get('health_status', 'N/A')}</p>
            <p>{system_summary.get('key_findings', '')}</p>
        </div>

        <div class="section">
            <h2>🚨 AI Fleet Risk Audit</h2>
            <table>
                <thead>
                    <tr>
                        <th>Bus ID</th>
                        <th>Route</th>
                        <th>Risk Score</th>
                        <th>Severity</th>
                        <th>Utilization</th>
                        <th>Avg Delay</th>
                        <th>Complaints</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for b in bus_insights:
        sev = b['severity'].lower()
        html_content += f"""
                    <tr>
                        <td><strong>{b['bus_id']}</strong></td>
                        <td>{b['route']}</td>
                        <td>{b['risk_score']}/100</td>
                        <td><span class="badge badge-{sev}">{b['severity']}</span></td>
                        <td>{b['evidence']['utilization']:.1f}%</td>
                        <td>{b['evidence']['avg_delay']:.1f} min</td>
                        <td>{int(b['evidence']['complaints'])}</td>
                    </tr>
        """
        
    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>⚡ Management Recommendations</h2>
            <ol>
    """
    
    for r in recommendations:
        html_content += f"<li><strong>[{r['category']}] {r['title']}</strong> (Urgency: {r['urgency']})<br><span style='color:#5D6D7E;'>{r['description']}</span><br><em>Expected Impact: {r['expected_impact']}</em></li><br>"
        
    html_content += """
            </ol>
        </div>

        <div class="footer">
            <p>Generated by AI College Transport Analyzer • Automated System Report</p>
        </div>
    </body>
    </html>
    """
    return html_content
