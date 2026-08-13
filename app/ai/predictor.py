import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def predict_demand(bus_usage_df, buses_df):
    """Predict next-day demand per bus using Random Forest."""
    if len(bus_usage_df) < 10:
        # Not enough data for prediction, return empty
        return pd.DataFrame()
        
    df = bus_usage_df.copy()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
    df = df.sort_values(by=['bus_id', 'date'])
    
    # Feature engineering
    df['day_of_week'] = df['date'].dt.dayofweek
    df['week_number'] = df['date'].dt.isocalendar().week.astype(int)
    
    # Simple label encoding for bus_id
    bus_ids = df['bus_id'].unique()
    bus_id_map = {b: i for i, b in enumerate(bus_ids)}
    df['bus_id_encoded'] = df['bus_id'].map(bus_id_map)
    
    # Rolling averages
    df['rolling_avg_3day'] = df.groupby('bus_id')['students_boarded'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['rolling_avg_5day'] = df.groupby('bus_id')['students_boarded'].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    
    # Fill NAs
    df = df.bfill().fillna(0)
    
    features = ['day_of_week', 'week_number', 'bus_id_encoded', 'rolling_avg_3day', 'rolling_avg_5day']
    X = df[features]
    y = df['students_boarded']
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Predict for "next day" (assuming it's a weekday 0-4)
    last_date = df['date'].max()
    next_day = last_date + pd.Timedelta(days=1)
    if next_day.dayofweek > 4:
        next_day += pd.Timedelta(days=8 - next_day.dayofweek)
        
    predictions = []
    
    for bus_id in bus_ids:
        bus_data = df[df['bus_id'] == bus_id].iloc[-1]
        
        # Calculate new rolling averages
        new_3day = df[df['bus_id'] == bus_id]['students_boarded'].tail(3).mean()
        new_5day = df[df['bus_id'] == bus_id]['students_boarded'].tail(5).mean()
        
        X_pred = pd.DataFrame([{
            'day_of_week': next_day.dayofweek,
            'week_number': next_day.isocalendar().week,
            'bus_id_encoded': bus_id_map[bus_id],
            'rolling_avg_3day': new_3day,
            'rolling_avg_5day': new_5day
        }])
        
        pred_passengers = int(model.predict(X_pred)[0])
        predictions.append({
            'bus_id': bus_id,
            'predicted_passengers': pred_passengers
        })
        
    pred_df = pd.DataFrame(predictions)
    pred_df = pred_df.merge(buses_df[['bus_id', 'total_capacity']], on='bus_id')
    pred_df['utilization_forecast'] = (pred_df['predicted_passengers'] / pred_df['total_capacity']) * 100
    
    def get_alert_level(util):
        if util > 100: return 'Critical'
        elif util > 85: return 'Warning'
        else: return 'Normal'
        
    pred_df['alert_level'] = pred_df['utilization_forecast'].apply(get_alert_level)
    return pred_df

def get_capacity_alerts(predictions_df):
    """Generate capacity alerts for predicted overcrowding."""
    alerts = []
    if predictions_df.empty:
        return alerts
        
    for _, row in predictions_df.iterrows():
        if row['alert_level'] in ['Critical', 'Warning']:
            alerts.append({
                'bus_id': row['bus_id'],
                'message': f"Expected utilization: {row['utilization_forecast']:.1f}% ({row['predicted_passengers']} students / {row['total_capacity']} capacity)",
                'severity': row['alert_level'].upper()
            })
    return alerts
