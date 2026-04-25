"""
AI Insight Generator
Auto-generates actionable summaries and recommendations
"""
import pandas as pd

class InsightGenerator:
    """Generate automated insights and recommendations."""
    
    def __init__(self):
        pass
    
    def generate_forecast_summary(self, forecast_results, trend_analysis):
        """Generate human-readable forecast summary."""
        
        patients = forecast_results.get('patients', {})
        icu = forecast_results.get('icu', {})
        
        total_predicted = patients.get('total_predicted', 0)
        avg_daily = patients.get('avg_daily', 0)
        
        trend_direction = trend_analysis.get('trend_direction', 'Stable')
        change_pct = trend_analysis.get('change_percentage', 0)
        
        summary = f"""
## 7-Day Forecast Summary

**Patient Inflow:** {total_predicted:,} patients expected over next 7 days 
(avg: {avg_daily:,} per day)

**Trend:** {trend_direction} ({change_pct:+.1f}% vs previous period)

**ICU Demand:** {icu.get('total_predicted', 0):,} ICU admissions expected

**Key Insights:**
"""
        
        # Add contextual insights
        insights = []
        
        if change_pct > 15:
            insights.append(f"• Significant patient increase predicted (+{change_pct:.1f}%). Prepare additional resources.")
        elif change_pct < -10:
            insights.append(f"• Patient volume declining ({change_pct:.1f}%). Opportunity for maintenance/staff training.")
        
        # Weekend analysis
        dates = patients.get('dates', [])
        weekend_days = sum(1 for d in dates if pd.to_datetime(d).weekday() >= 5)
        if weekend_days > 0:
            insights.append(f"• {weekend_days} weekend days in forecast period. Emergency cases typically 15-20% higher on weekends.")
        
        if not insights:
            insights.append("• Stable patient flow expected. Maintain current staffing levels.")
        
        return summary + '\n'.join(insights)
    
    def generate_resource_alert(self, bed_status, staff_schedule):
        """Generate resource shortage alerts."""
        
        alerts = []
        
        # Bed alerts
        general = bed_status.get('general_ward', {})
        icu = bed_status.get('icu', {})
        
        if general.get('status') == 'Critical':
            alerts.append({
                'level': 'CRITICAL',
                'type': 'Bed Shortage',
                'message': f"General ward at {general.get('utilization', 0)}% capacity. Initiate discharge planning and consider temporary beds."
            })
        elif general.get('status') == 'High':
            alerts.append({
                'level': 'WARNING',
                'type': 'Bed Pressure',
                'message': f"General ward utilization at {general.get('utilization', 0)}%. Monitor closely."
            })
        
        if icu.get('status') == 'Critical':
            alerts.append({
                'level': 'CRITICAL',
                'type': 'ICU Shortage',
                'message': f"ICU at {icu.get('utilization', 0)}% capacity! Consider transfers to other facilities."
            })
        
        # Staff alerts
        schedule = staff_schedule.get('daily_schedule', [])
        high_cost_days = [d for d in schedule if d.get('additional_cost', 0) > 1500]
        
        if high_cost_days:
            alerts.append({
                'level': 'WARNING',
                'type': 'Staffing Cost',
                'message': f"{len(high_cost_days)} days require expensive additional staffing. Review allocation efficiency."
            })
        
        if not alerts:
            alerts.append({
                'level': 'INFO',
                'type': 'Resources',
                'message': "All resource levels within normal parameters."
            })
        
        return alerts
    
    def generate_action_items(self, forecast_results, bed_status, staff_schedule, anomaly_status):
        """Generate prioritized action items."""
        
        actions = []
        
        # Priority 1: Critical issues
        if anomaly_status.get('status') == 'CRITICAL':
            actions.append({
                'priority': 1,
                'action': 'Activate emergency protocols - multiple critical thresholds breached',
                'owner': 'Hospital Admin',
                'deadline': 'Immediate'
            })
        
        # Bed shortages
        icu = bed_status.get('icu', {})
        if icu.get('status') == 'Critical':
            actions.append({
                'priority': 1,
                'action': 'Contact nearby hospitals for ICU bed availability',
                'owner': 'Bed Management',
                'deadline': 'Within 2 hours'
            })
        
        general = bed_status.get('general_ward', {})
        if general.get('status') == 'Critical':
            actions.append({
                'priority': 1,
                'action': 'Expedite patient discharges and cancel elective procedures',
                'owner': 'Medical Director',
                'deadline': 'Today'
            })
        
        # Staffing needs
        schedule = staff_schedule.get('daily_schedule', [])
        extra_staff_days = [d for d in schedule if d.get('extra_doctors_needed', 0) > 0]
        if extra_staff_days:
            actions.append({
                'priority': 2,
                'action': f'Arrange {len(extra_staff_days)} days of locum/contract doctor coverage',
                'owner': 'HR/Staffing',
                'deadline': 'Within 48 hours'
            })
        
        # Trend-based actions
        trend = forecast_results.get('patients', {})
        predictions = trend.get('predictions', [])
        if predictions and max(predictions) > 350:
            peak_day = predictions.index(max(predictions))
            actions.append({
                'priority': 2,
                'action': f'Peak demand expected on Day {peak_day + 1}. Ensure full staffing and bed availability.',
                'owner': 'Operations',
                'deadline': 'Day of peak'
            })
        
        # If no critical actions
        if not actions:
            actions.append({
                'priority': 3,
                'action': 'Continue routine monitoring and maintenance',
                'owner': 'All Departments',
                'deadline': 'Ongoing'
            })
        
        return sorted(actions, key=lambda x: x['priority'])
    
    def generate_executive_summary(self, all_data):
        """Generate executive summary for leadership."""
        
        forecast = all_data.get('forecast', {})
        bed = all_data.get('bed_status', {})
        staff = all_data.get('staff_schedule', {})
        anomaly = all_data.get('anomaly_status', {})
        
        summary = f"""
# MediOptima Executive Summary
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## System Status: {anomaly.get('status', 'UNKNOWN')}

### Forecast Overview
- **Next 7 Days:** {forecast.get('patients', {}).get('total_predicted', 0):,} patients expected
- **Trend:** {all_data.get('trend', {}).get('trend_direction', 'Stable')} ({all_data.get('trend', {}).get('change_percentage', 0):+.1f}%)
- **Peak Demand:** {max(forecast.get('patients', {}).get('predictions', [0])):,} patients (Day {forecast.get('patients', {}).get('predictions', [0]).index(max(forecast.get('patients', {}).get('predictions', [0]))) + 1 if forecast.get('patients', {}).get('predictions') else 0})

### Resource Status
| Resource | Utilization | Status |
|----------|-------------|--------|
| General Beds | {bed.get('general_ward', {}).get('utilization', 0)}% | {bed.get('general_ward', {}).get('status', 'Unknown')} |
| ICU Beds | {bed.get('icu', {}).get('utilization', 0)}% | {bed.get('icu', {}).get('status', 'Unknown')} |
| Additional Staff Cost | ₹{staff.get('total_weekly_cost', 0):,} | {'High' if staff.get('total_weekly_cost', 0) > 5000 else 'Normal'} |

### Immediate Actions Required
"""
        
        actions = all_data.get('action_items', [])
        for action in actions[:5]:
            summary += f"\n{action['priority']}. {action['action']} ({action['owner']})"
        
        return summary
    
    def generate_all_insights(self, forecast_results, trend, bed_status, staff_schedule, anomaly_status):
        """Generate complete insight package."""
        
        return {
            'forecast_summary': self.generate_forecast_summary(forecast_results, trend),
            'resource_alerts': self.generate_resource_alert(bed_status, staff_schedule),
            'action_items': self.generate_action_items(forecast_results, bed_status, staff_schedule, anomaly_status),
            'anomaly_status': anomaly_status
        }
