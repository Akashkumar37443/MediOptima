"""
Module 3: Staff Scheduling Optimization
Linear Programming optimization using PuLP
"""
import pandas as pd
import numpy as np
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value, LpInteger

class StaffOptimizer:
    """Optimize doctor and nurse scheduling using Linear Programming."""
    
    def __init__(self):
        self.problem = None
        self.solution = None
        self.constraints = {
            'doctor_patient_ratio': 1/20,  # 1 doctor per 20 patients
            'nurse_patient_ratio': 1/8,     # 1 nurse per 8 patients
            'icu_nurse_patient_ratio': 1/2,  # 1 ICU nurse per 2 ICU patients
            'max_doctor_hours': 12,
            'max_nurse_hours': 12,
            'doctor_hourly_cost': 150,  # per hour
            'nurse_hourly_cost': 80,    # per hour
            'icu_nurse_hourly_cost': 120  # per hour
        }
    
    def optimize_daily_staffing(self, predicted_patients, predicted_icu, 
                               current_doctors, current_nurses, current_icu_nurses):
        """
        Optimize staff allocation for a day shift.
        
        Objective: Minimize cost while meeting all constraints
        """
        # Create LP problem
        prob = LpProblem("Staff_Optimization", LpMinimize)
        
        # Decision variables: number of staff to schedule
        doctors_needed = LpVariable("Doctors_Needed", lowBound=0, cat=LpInteger)
        nurses_needed = LpVariable("Nurses_Needed", lowBound=0, cat=LpInteger)
        icu_nurses_needed = LpVariable("ICU_Nurses_Needed", lowBound=0, cat=LpInteger)
        
        # Additional staff (if current insufficient)
        extra_doctors = LpVariable("Extra_Doctors", lowBound=0, cat=LpInteger)
        extra_nurses = LpVariable("Extra_Nurses", lowBound=0, cat=LpInteger)
        extra_icu_nurses = LpVariable("Extra_ICU_Nurses", lowBound=0, cat=LpInteger)
        
        # Calculate minimum required staff
        min_doctors = max(3, int(np.ceil(predicted_patients * self.constraints['doctor_patient_ratio'])))
        min_nurses = max(8, int(np.ceil(predicted_patients * self.constraints['nurse_patient_ratio'])))
        min_icu_nurses = max(4, int(np.ceil(predicted_icu * self.constraints['icu_nurse_patient_ratio'])))
        
        # Objective: Minimize cost of additional staff
        prob += (
            extra_doctors * self.constraints['doctor_hourly_cost'] * 8 +
            extra_nurses * self.constraints['nurse_hourly_cost'] * 8 +
            extra_icu_nurses * self.constraints['icu_nurse_hourly_cost'] * 8
        ), "Total_Additional_Staff_Cost"
        
        # Constraints
        # Doctor coverage
        prob += doctors_needed + extra_doctors >= min_doctors, "Doctor_Coverage"
        prob += doctors_needed <= current_doctors, "Doctor_Availability"
        
        # Nurse coverage
        prob += nurses_needed + extra_nurses >= min_nurses, "Nurse_Coverage"
        prob += nurses_needed <= current_nurses, "Nurse_Availability"
        
        # ICU Nurse coverage
        prob += icu_nurses_needed + extra_icu_nurses >= min_icu_nurses, "ICU_Nurse_Coverage"
        prob += icu_nurses_needed <= current_icu_nurses, "ICU_Nurse_Availability"
        
        # Solve
        prob.solve()
        
        # Extract results
        result = {
            'status': LpStatus[prob.status],
            'min_doctors_required': min_doctors,
            'min_nurses_required': min_nurses,
            'min_icu_nurses_required': min_icu_nurses,
            'doctors_scheduled': int(value(doctors_needed)) if value(doctors_needed) else 0,
            'nurses_scheduled': int(value(nurses_needed)) if value(nurses_needed) else 0,
            'icu_nurses_scheduled': int(value(icu_nurses_needed)) if value(icu_nurses_needed) else 0,
            'extra_doctors_needed': int(value(extra_doctors)) if value(extra_doctors) else 0,
            'extra_nurses_needed': int(value(extra_nurses)) if value(extra_nurses) else 0,
            'extra_icu_nurses_needed': int(value(extra_icu_nurses)) if value(extra_icu_nurses) else 0,
            'additional_cost': round(
                (value(extra_doctors) or 0) * self.constraints['doctor_hourly_cost'] * 8 +
                (value(extra_nurses) or 0) * self.constraints['nurse_hourly_cost'] * 8 +
                (value(extra_icu_nurses) or 0) * self.constraints['icu_nurse_hourly_cost'] * 8, 2
            ),
            'constraints_met': LpStatus[prob.status] == 'Optimal'
        }
        
        return result
    
    def generate_weekly_schedule(self, patient_forecast, icu_forecast, base_staffing):
        """Generate 7-day optimized schedule."""
        
        weekly_schedule = []
        total_additional_cost = 0
        
        for i in range(7):
            day_forecast = {
                'patients': patient_forecast['predictions'][i] if i < len(patient_forecast.get('predictions', [])) else 200,
                'icu': icu_forecast['predictions'][i] if i < len(icu_forecast.get('predictions', [])) else 20
            }
            
            day_opt = self.optimize_daily_staffing(
                predicted_patients=day_forecast['patients'],
                predicted_icu=day_forecast['icu'],
                current_doctors=base_staffing['doctors'],
                current_nurses=base_staffing['nurses'],
                current_icu_nurses=base_staffing['icu_nurses']
            )
            
            day_opt['day'] = i + 1
            day_opt['date'] = patient_forecast.get('dates', ['Day ' + str(i+1)] * 7)[i]
            day_opt['predicted_patients'] = day_forecast['patients']
            day_opt['predicted_icu'] = day_forecast['icu']
            
            weekly_schedule.append(day_opt)
            total_additional_cost += day_opt['additional_cost']
        
        return {
            'daily_schedule': weekly_schedule,
            'total_weekly_cost': round(total_additional_cost, 2),
            'avg_daily_cost': round(total_additional_cost / 7, 2)
        }
    
    def get_staffing_recommendations(self, schedule_result):
        """Generate human-readable recommendations."""
        
        recommendations = []
        schedule = schedule_result['daily_schedule']
        
        # Check for days requiring extra staff
        extra_days = [day for day in schedule if day['extra_doctors_needed'] > 0 or 
                     day['extra_nurses_needed'] > 0 or day['extra_icu_nurses_needed'] > 0]
        
        if extra_days:
            recommendations.append(
                f"⚠️ {len(extra_days)} days require additional staff. Consider hiring temporary staff or reallocating from other departments."
            )
        
        # Check ICU capacity
        icu_strain_days = [day for day in schedule if day['extra_icu_nurses_needed'] > 2]
        if icu_strain_days:
            recommendations.append(
                f"🚨 ICU nurse shortage predicted on {len(icu_strain_days)} days. Priority: Recruit ICU nurses immediately."
            )
        
        # Cost optimization
        if schedule_result['total_weekly_cost'] > 5000:
            recommendations.append(
                f"💰 High additional staffing cost (₹{schedule_result['total_weekly_cost']}/week). Review shift patterns for optimization."
            )
        
        if not recommendations:
            recommendations.append("✅ Current staffing levels adequate for predicted demand.")
        
        return recommendations
