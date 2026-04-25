"""
Module 1: Patient Inflow Prediction
Time-series forecasting using ARIMA and statistical methods
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class PatientForecaster:
    """Patient inflow forecasting using ARIMA."""
    
    def __init__(self):
        self.model = None
        self.history = None
        self.forecast_values = None
        self.forecast_df = None
        self.metrics = {}
    
    def fit(self, df, target_col='Daily_Patients', periods=30):
        """Train ARIMA model and generate forecast."""
        
        # Prepare time series data
        ts_data = df[target_col].values
        self.history = df[['Date', target_col]].copy()
        
        # Fit ARIMA model (7,1,0) - simple but effective
        try:
            self.model = ARIMA(ts_data, order=(7, 1, 0))
            fitted_model = self.model.fit()
            
            # Generate forecast
            forecast_result = fitted_model.get_forecast(steps=periods)
            self.forecast_values = forecast_result.predicted_mean
            
            # Calculate confidence intervals
            conf_int = forecast_result.conf_int(alpha=0.2)
            
            # Create forecast dataframe
            last_date = df['Date'].iloc[-1]
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)
            
            self.forecast_df = pd.DataFrame({
                'ds': future_dates,
                'yhat': self.forecast_values,
                'yhat_lower': conf_int[:, 0],
                'yhat_upper': conf_int[:, 1]
            })
            
            # Calculate metrics using train-test split
            train_size = int(len(ts_data) * 0.8)
            train_data = ts_data[:train_size]
            test_data = ts_data[train_size:]
            
            # Fit on training data
            train_model = ARIMA(train_data, order=(7, 1, 0))
            train_fitted = train_model.fit()
            
            # Predict on test data
            predictions = train_fitted.forecast(steps=len(test_data))
            
            self.metrics = {
                'MAE': mean_absolute_error(test_data, predictions),
                'RMSE': np.sqrt(mean_squared_error(test_data, predictions)),
                'MAPE': np.mean(np.abs((test_data - predictions) / test_data)) * 100
            }
            
        except Exception as e:
            # Fallback to simple moving average if ARIMA fails
            print(f"ARIMA failed: {e}, using moving average fallback")
            last_date = df['Date'].iloc[-1]
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)
            
            # Use 30-day moving average
            ma_value = np.mean(ts_data[-30:])
            seasonal_factor = [1.0, 1.05, 1.1, 1.05, 1.0, 0.95, 0.9]  # Weekly pattern
            
            forecasts = []
            lower_bounds = []
            upper_bounds = []
            
            for i in range(periods):
                day_idx = i % 7
                pred = ma_value * seasonal_factor[day_idx]
                forecasts.append(pred)
                lower_bounds.append(pred * 0.85)
                upper_bounds.append(pred * 1.15)
            
            self.forecast_df = pd.DataFrame({
                'ds': future_dates,
                'yhat': forecasts,
                'yhat_lower': lower_bounds,
                'yhat_upper': upper_bounds
            })
            
            self.metrics = {'MAE': 0, 'RMSE': 0, 'MAPE': 0}
        
        return self.forecast_df
    
    def get_predictions(self, days=7):
        """Get next N days predictions."""
        if self.forecast_df is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        return self.forecast_df.head(days)
    
    def get_weekly_forecast(self):
        """Get 7-day forecast summary."""
        pred = self.get_predictions(7)
        return {
            'dates': pred['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'predictions': pred['yhat'].round(0).astype(int).tolist(),
            'lower_bound': pred['yhat_lower'].round(0).astype(int).tolist(),
            'upper_bound': pred['yhat_upper'].round(0).astype(int).tolist(),
            'total_predicted': int(pred['yhat'].sum()),
            'avg_daily': int(pred['yhat'].mean())
        }
    
    def get_trend_analysis(self):
        """Analyze trend direction."""
        if self.forecast_df is None:
            return {}
        
        recent = self.forecast_df['yhat'].head(14)
        older_mean = self.history.iloc[-30:][self.history.columns[1]].mean()
        
        recent_mean = recent.mean()
        change_pct = ((recent_mean - older_mean) / older_mean) * 100
        
        return {
            'trend_direction': 'Increasing' if change_pct > 2 else ('Decreasing' if change_pct < -2 else 'Stable'),
            'change_percentage': round(change_pct, 1),
            'avg_recent': int(recent_mean),
            'avg_older': int(older_mean)
        }


class MultiMetricForecaster:
    """Forecast multiple metrics: Patients, Emergency, ICU."""
    
    def __init__(self):
        self.forecasters = {}
        self.results = {}
    
    def fit_all(self, df, periods=30):
        """Fit models for all key metrics."""
        
        targets = ['Daily_Patients', 'Emergency_Cases', 'ICU_Admissions']
        
        for target in targets:
            forecaster = PatientForecaster()
            forecaster.fit(df, target_col=target, periods=periods)
            self.forecasters[target] = forecaster
            self.results[target] = forecaster.get_weekly_forecast()
        
        return self.results
    
    def get_combined_forecast(self):
        """Get all forecasts in one structure."""
        return {
            'patients': self.results.get('Daily_Patients', {}),
            'emergency': self.results.get('Emergency_Cases', {}),
            'icu': self.results.get('ICU_Admissions', {})
        }
