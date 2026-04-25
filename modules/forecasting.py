"""
Module 1: Patient Inflow Prediction
Time-series forecasting using Prophet and statistical methods
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class PatientForecaster:
    """Patient inflow forecasting using Prophet."""
    
    def __init__(self):
        self.model = None
        self.forecast_df = None
        self.metrics = {}
    
    def prepare_data(self, df, target_col='Daily_Patients'):
        """Prepare data for Prophet model."""
        prophet_df = df[['Date', target_col]].copy()
        prophet_df.columns = ['ds', 'y']
        return prophet_df
    
    def fit(self, df, target_col='Daily_Patients', periods=30):
        """Train Prophet model and generate forecast."""
        
        # Prepare data
        train_df = self.prepare_data(df, target_col)
        
        # Initialize and fit Prophet model
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05
        )
        
        # Add holiday effects
        self.model.add_country_holidays(country_name='IN')
        
        # Fit model
        self.model.fit(train_df)
        
        # Create future dataframe for prediction
        future = self.model.make_future_dataframe(periods=periods)
        self.forecast_df = self.model.predict(future)
        
        # Calculate metrics on training data
        train_size = int(len(train_df) * 0.8)
        train_subset = train_df.iloc[:train_size]
        test_subset = train_df.iloc[train_size:]
        
        # Retrain on subset for validation
        temp_model = Prophet(yearly_seasonality=True, weekly_seasonality=True, 
                            daily_seasonality=False, seasonality_mode='multiplicative')
        temp_model.fit(train_subset)
        
        future_val = temp_model.make_future_dataframe(periods=len(test_subset))
        forecast_val = temp_model.predict(future_val)
        
        y_true = test_subset['y'].values
        y_pred = forecast_val['yhat'].iloc[-len(test_subset):].values
        
        self.metrics = {
            'MAE': mean_absolute_error(y_true, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAPE': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }
        
        return self.forecast_df
    
    def get_predictions(self, days=7):
        """Get next N days predictions."""
        if self.forecast_df is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        future = self.forecast_df[self.forecast_df['ds'] > self.forecast_df['ds'].max() - pd.Timedelta(days=days)]
        return future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
    
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
        
        recent = self.forecast_df['yhat'].tail(14)
        older = self.forecast_df['yhat'].iloc[-30:-14]
        
        change_pct = ((recent.mean() - older.mean()) / older.mean()) * 100
        
        return {
            'trend_direction': 'Increasing' if change_pct > 2 else ('Decreasing' if change_pct < -2 else 'Stable'),
            'change_percentage': round(change_pct, 1),
            'avg_recent': int(recent.mean()),
            'avg_older': int(older.mean())
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
