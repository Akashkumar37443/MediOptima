"""
Module 4: Surge & Anomaly Detection
Detect abnormal spikes using Z-score and Isolation Forest
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats

class AnomalyDetector:
    """Detect surge patterns and anomalies in hospital data."""
    
    def __init__(self, z_threshold=2.5):
        self.z_threshold = z_threshold
        self.isolation_model = None
        self.baseline_stats = {}
    
    def fit_baseline(self, df, columns=['Daily_Patients', 'Emergency_Cases', 'ICU_Admissions']):
        """Calculate baseline statistics for anomaly detection."""
        
        for col in columns:
            self.baseline_stats[col] = {
                'mean': df[col].mean(),
                'std': df[col].std(),
                'q95': df[col].quantile(0.95),
                'q99': df[col].quantile(0.99)
            }
        
        # Fit Isolation Forest for multivariate detection
        self.isolation_model = IsolationForest(
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
            n_estimators=100
        )
        self.isolation_model.fit(df[columns])
        
        return self.baseline_stats
    
    def detect_zscore_anomalies(self, df, column='Daily_Patients'):
        """Detect anomalies using Z-score method."""
        
        if column not in self.baseline_stats:
            self.fit_baseline(df)
        
        stats_dict = self.baseline_stats[column]
        z_scores = np.abs((df[column] - stats_dict['mean']) / stats_dict['std'])
        
        anomalies = df[z_scores > self.z_threshold].copy()
        anomalies['z_score'] = z_scores[z_scores > self.z_threshold]
        anomalies['severity'] = anomalies['z_score'].apply(
            lambda x: 'CRITICAL' if x > 4 else ('HIGH' if x > 3 else 'MEDIUM')
        )
        
        return anomalies[['Date', column, 'z_score', 'severity']]
    
    def detect_isolation_anomalies(self, df, columns=['Daily_Patients', 'Emergency_Cases', 'ICU_Admissions']):
        """Detect anomalies using Isolation Forest."""
        
        if self.isolation_model is None:
            self.fit_baseline(df, columns)
        
        predictions = self.isolation_model.predict(df[columns])
        scores = self.isolation_model.score_samples(df[columns])
        
        anomalies = df[predictions == -1].copy()
        anomalies['anomaly_score'] = scores[predictions == -1]
        anomalies['severity'] = anomalies['anomaly_score'].apply(
            lambda x: 'CRITICAL' if x < -0.6 else ('HIGH' if x < -0.5 else 'MEDIUM')
        )
        
        return anomalies[['Date'] + columns + ['anomaly_score', 'severity']]
    
    def detect_surge_pattern(self, df, window=7):
        """Detect sustained surge patterns (not just single-day spikes)."""
        
        # Calculate rolling statistics
        df_temp = df.copy()
        df_temp['rolling_mean'] = df_temp['Daily_Patients'].rolling(window=window).mean()
        df_temp['rolling_std'] = df_temp['Daily_Patients'].rolling(window=window).std()
        
        # Calculate deviation from rolling mean
        df_temp['deviation'] = (df_temp['Daily_Patients'] - df_temp['rolling_mean']) / df_temp['rolling_std']
        
        # Find sustained surge (3+ consecutive days above threshold)
        surge_threshold = 1.5
        df_temp['is_surge'] = df_temp['deviation'] > surge_threshold
        
        # Identify surge periods
        surge_periods = []
        in_surge = False
        start_idx = None
        
        for idx, row in df_temp.iterrows():
            if row['is_surge'] and not in_surge:
                in_surge = True
                start_idx = idx
            elif not row['is_surge'] and in_surge:
                in_surge = False
                if start_idx is not None:
                    duration = df_temp.index.get_loc(idx) - df_temp.index.get_loc(start_idx)
                    if duration >= 3:  # Minimum 3 days for a surge
                        surge_periods.append({
                            'start_date': df_temp.loc[start_idx, 'Date'],
                            'end_date': df_temp.loc[df_temp.index[df_temp.index.get_loc(idx) - 1], 'Date'],
                            'duration_days': duration,
                            'peak_patients': int(df_temp.loc[start_idx:idx, 'Daily_Patients'].max()),
                            'avg_deviation': round(df_temp.loc[start_idx:idx, 'deviation'].mean(), 2)
                        })
        
        return surge_periods
    
    def analyze_forecast_risk(self, forecast_df):
        """Analyze forecast for potential future risks."""
        
        # Get last 30 days of historical data and future predictions
        future = forecast_df[forecast_df['ds'] > forecast_df['ds'].max() - pd.Timedelta(days=37)]
        
        recent_mean = future['yhat'].iloc[:7].mean()
        future_mean = future['yhat'].iloc[7:14].mean()
        
        change_pct = ((future_mean - recent_mean) / recent_mean) * 100
        
        risk_level = 'LOW'
        alerts = []
        
        if change_pct > 30:
            risk_level = 'CRITICAL'
            alerts.append(f"Patient surge predicted: {change_pct:.1f}% increase expected")
        elif change_pct > 15:
            risk_level = 'HIGH'
            alerts.append(f"Significant patient increase: {change_pct:.1f}% expected")
        elif change_pct > 5:
            risk_level = 'MEDIUM'
            alerts.append(f"Moderate patient increase: {change_pct:.1f}% expected")
        
        # Check if upper bound exceeds critical threshold
        max_upper = future['yhat_upper'].max()
        if max_upper > self.baseline_stats.get('Daily_Patients', {}).get('q99', 400):
            alerts.append("Peak demand may exceed 99th percentile capacity")
        
        return {
            'risk_level': risk_level,
            'predicted_change_pct': round(change_pct, 1),
            'alerts': alerts,
            'recent_avg': int(recent_mean),
            'predicted_avg': int(future_mean)
        }
    
    def get_current_status(self, latest_data):
        """Get real-time anomaly status for latest data."""
        
        latest = latest_data.iloc[-1]
        
        # Check against thresholds
        patient_threshold = self.baseline_stats.get('Daily_Patients', {}).get('q95', 300)
        emergency_threshold = self.baseline_stats.get('Emergency_Cases', {}).get('q95', 80)
        icu_threshold = self.baseline_stats.get('ICU_Admissions', {}).get('q95', 35)
        
        status_flags = {
            'patient_surge': latest['Daily_Patients'] > patient_threshold,
            'emergency_surge': latest['Emergency_Cases'] > emergency_threshold,
            'icu_surge': latest['ICU_Admissions'] > icu_threshold,
            'bed_shortage': latest['Available_Beds'] < 30,
            'icu_bed_shortage': latest['Available_ICU_Beds'] < 5
        }
        
        # Determine overall status
        critical_count = sum(1 for v in status_flags.values() if v)
        
        if critical_count >= 3:
            overall_status = 'CRITICAL'
        elif critical_count >= 2:
            overall_status = 'HIGH'
        elif critical_count >= 1:
            overall_status = 'ELEVATED'
        else:
            overall_status = 'NORMAL'
        
        return {
            'status': overall_status,
            'flags': status_flags,
            'latest_date': str(latest['Date']),
            'latest_values': {
                'patients': int(latest['Daily_Patients']),
                'emergency': int(latest['Emergency_Cases']),
                'icu': int(latest['ICU_Admissions']),
                'available_beds': int(latest['Available_Beds']),
                'available_icu_beds': int(latest['Available_ICU_Beds'])
            },
            'thresholds': {
                'patient_threshold': int(patient_threshold),
                'emergency_threshold': int(emergency_threshold),
                'icu_threshold': int(icu_threshold)
            }
        }
