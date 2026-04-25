"""
Synthetic Hospital Data Generator for MediOptima
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_hospital_data(start_date='2022-01-01', end_date='2024-04-30'):
    """Generate realistic synthetic hospital data with seasonality and trends."""
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(date_range)
    
    # Base seasonality patterns
    day_of_year = date_range.dayofyear
    day_of_week = date_range.dayofweek
    month = date_range.month
    
    # Winter peak (flu season), summer dip
    seasonal_pattern = 50 * np.sin(2 * np.pi * (day_of_year - 15) / 365) + \
                      30 * np.sin(4 * np.pi * day_of_year / 365)
    
    # Weekly pattern - more admissions on weekdays
    weekly_pattern = np.where(day_of_week < 5, 15, -20)
    
    # Trend: gradual increase over years
    trend = np.linspace(0, 80, n_days)
    
    # Base patient count
    base_patients = 200 + seasonal_pattern + weekly_pattern + trend
    
    # Add noise
    noise = np.random.normal(0, 15, n_days)
    daily_patients = np.maximum(base_patients + noise, 50).astype(int)
    
    # Emergency cases (20-30% of total, higher on weekends/holidays)
    emergency_rate = 0.25 + 0.05 * np.sin(2 * np.pi * day_of_year / 7)
    emergency_cases = (daily_patients * emergency_rate + np.random.normal(0, 5, n_days)).astype(int)
    
    # ICU admissions (8-15% of total)
    icu_rate = 0.10 + 0.02 * np.where(month.isin([12, 1, 2]), 1, 0)  # Higher in winter
    icu_admissions = (daily_patients * icu_rate + np.random.normal(0, 2, n_days)).astype(int)
    
    # Discharge count (correlated with previous day admissions)
    discharge_lag = np.roll(daily_patients, 3) * 0.85  # Avg 3-day stay
    discharge_count = (discharge_lag + np.random.normal(0, 10, n_days)).astype(int)
    
    # Available beds (fluctuates based on demand)
    total_beds = 350
    total_icu_beds = 45
    
    available_beds = np.maximum(total_beds - daily_patients * 0.6 - np.random.normal(0, 20, n_days), 20).astype(int)
    available_icu_beds = np.maximum(total_icu_beds - icu_admissions - np.random.normal(0, 5, n_days), 2).astype(int)
    
    # Staff counts
    base_doctors = 25
    base_nurses = 80
    base_icu_nurses = 18
    
    doctors = (base_doctors + daily_patients / 25).astype(int)
    nurses = (base_nurses + daily_patients / 8).astype(int)
    icu_nurses = (base_icu_nurses + icu_admissions / 2).astype(int)
    
    # Public holidays
    holidays = [
        '01-01', '01-26', '08-15', '10-02', '12-25',  # India major holidays
        '03-08', '04-14', '05-01', '10-20', '11-12', '12-31'
    ]
    is_holiday = date_range.strftime('%m-%d').isin(holidays).astype(int)
    
    # Weather (optional) - temperature affects respiratory cases
    temperature = 25 + 10 * np.sin(2 * np.pi * (day_of_year - 100) / 365) + np.random.normal(0, 3, n_days)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': date_range,
        'Daily_Patients': daily_patients,
        'Emergency_Cases': emergency_cases,
        'ICU_Admissions': icu_admissions,
        'Discharge_Count': discharge_count,
        'Available_Beds': available_beds,
        'Available_ICU_Beds': available_icu_beds,
        'Total_Beds': total_beds,
        'Total_ICU_Beds': total_icu_beds,
        'Doctors_On_Duty': doctors,
        'Nurses_On_Duty': nurses,
        'ICU_Nurses': icu_nurses,
        'Is_Holiday': is_holiday,
        'Temperature': temperature.round(1),
        'DayOfWeek': day_of_week,
        'Month': month,
        'DayOfYear': day_of_year
    })
    
    # Add some anomaly spikes (surge events)
    anomaly_indices = np.random.choice(n_days, size=8, replace=False)
    for idx in anomaly_indices:
        df.loc[idx, 'Daily_Patients'] = int(df.loc[idx, 'Daily_Patients'] * 1.5)
        df.loc[idx, 'Emergency_Cases'] = int(df.loc[idx, 'Emergency_Cases'] * 1.8)
        df.loc[idx, 'ICU_Admissions'] = int(df.loc[idx, 'ICU_Admissions'] * 1.4)
    
    return df

if __name__ == '__main__':
    df = generate_hospital_data()
    df.to_csv('C:\\Users\\Akash thakur\\CascadeProjects\\MediOptima\\hospital_data.csv', index=False)
    print(f"Generated {len(df)} days of hospital data")
    print(df.head())
    print(f"\nSurge events detected: {len(df[df['Daily_Patients'] > df['Daily_Patients'].quantile(0.98)])}")
