"""
Module 2: Bed Requirement Estimation
Calculates required beds with emergency buffer
"""
import pandas as pd
import numpy as np

class BedOptimizer:
    """Calculate bed requirements and shortage risks."""
    
    def __init__(self, total_beds=350, total_icu_beds=45):
        self.total_beds = total_beds
        self.total_icu_beds = total_icu_beds
        self.emergency_buffer_pct = 0.15  # 15% emergency margin
    
    def calculate_bed_needs(self, predicted_patients, expected_discharges, 
                           current_occupied, avg_los_days=3.5):
        """
        Calculate bed requirements with buffer.
        
        Formula: Required = (Predicted - Expected Discharges) + Emergency Buffer
        """
        # Net new patients expected
        net_inflow = predicted_patients - expected_discharges
        
        # Account for current occupancy
        projected_occupancy = current_occupied + net_inflow
        
        # Add emergency buffer (15%)
        required_beds = projected_occupancy * (1 + self.emergency_buffer_pct)
        
        return {
            'predicted_patients': int(predicted_patients),
            'expected_discharges': int(expected_discharges),
            'net_inflow': int(net_inflow),
            'current_occupied': int(current_occupied),
            'projected_occupancy': int(projected_occupancy),
            'required_beds_with_buffer': int(required_beds),
            'buffer_amount': int(projected_occupancy * self.emergency_buffer_pct)
        }
    
    def calculate_icu_needs(self, predicted_icu, expected_icu_discharges, 
                             current_icu_occupied):
        """Calculate ICU bed requirements."""
        
        net_icu_inflow = predicted_icu - expected_icu_discharges
        projected_icu_occupancy = current_icu_occupied + net_icu_inflow
        
        # Higher buffer for ICU (20%)
        required_icu = projected_icu_occupancy * 1.20
        
        return {
            'predicted_icu': int(predicted_icu),
            'expected_discharges': int(expected_icu_discharges),
            'net_inflow': int(net_icu_inflow),
            'current_occupied': int(current_icu_occupied),
            'projected_occupancy': int(projected_icu_occupancy),
            'required_icu_with_buffer': int(required_icu),
            'buffer_amount': int(projected_icu_occupancy * 0.20)
        }
    
    def assess_shortage_risk(self, required_beds, available_beds):
        """Assess shortage risk level."""
        shortage = required_beds - available_beds
        utilization = (required_beds / self.total_beds) * 100
        
        if shortage > 0:
            risk_level = 'CRITICAL' if shortage > 30 else ('HIGH' if shortage > 15 else 'MEDIUM')
        else:
            risk_level = 'LOW'
        
        return {
            'shortage': int(max(0, shortage)),
            'surplus': int(max(0, -shortage)),
            'utilization_percentage': round(utilization, 1),
            'risk_level': risk_level,
            'available_beds': available_beds,
            'required_beds': required_beds
        }
    
    def generate_7day_bed_forecast(self, forecast_data, current_data):
        """Generate 7-day bed requirement forecast."""
        
        daily_forecasts = []
        
        for i in range(7):
            predicted = forecast_data['predictions'][i] if i < len(forecast_data.get('predictions', [])) else 0
            
            # Estimate discharges based on avg LOS
            expected_discharge = int(predicted * 0.75)  # Simplified assumption
            
            # Assume current occupancy changes daily
            current_occ = current_data.get('occupied_general', 250) + (i * 5)
            
            bed_calc = self.calculate_bed_needs(predicted, expected_discharge, current_occ)
            shortage = self.assess_shortage_risk(bed_calc['required_beds_with_buffer'], 
                                                self.total_beds - current_occ)
            
            daily_forecasts.append({
                'day': i + 1,
                'date': forecast_data['dates'][i] if i < len(forecast_data.get('dates', [])) else 'TBD',
                'predicted_patients': bed_calc['predicted_patients'],
                'required_beds': bed_calc['required_beds_with_buffer'],
                'available_beds': self.total_beds - current_occ,
                'shortage_risk': shortage['risk_level'],
                'utilization': shortage['utilization_percentage']
            })
        
        return daily_forecasts
    
    def get_capacity_summary(self, current_df, forecast_df):
        """Get overall capacity summary."""
        
        latest = current_df.iloc[-1]
        
        current_general_occupied = latest['Total_Beds'] - latest['Available_Beds']
        current_icu_occupied = latest['Total_ICU_Beds'] - latest['Available_ICU_Beds']
        
        general_util = (current_general_occupied / self.total_beds) * 100
        icu_util = (current_icu_occupied / self.total_icu_beds) * 100
        
        # Predict next day
        next_day_patients = forecast_df['yhat'].iloc[-30] if len(forecast_df) > 30 else current_general_occupied
        
        return {
            'general_ward': {
                'total': self.total_beds,
                'occupied': int(current_general_occupied),
                'available': int(latest['Available_Beds']),
                'utilization': round(general_util, 1),
                'status': 'Critical' if general_util > 95 else ('High' if general_util > 85 else 'Normal')
            },
            'icu': {
                'total': self.total_icu_beds,
                'occupied': int(current_icu_occupied),
                'available': int(latest['Available_ICU_Beds']),
                'utilization': round(icu_util, 1),
                'status': 'Critical' if icu_util > 95 else ('High' if icu_util > 85 else 'Normal')
            },
            'next_day_prediction': int(next_day_patients)
        }
