"""
MediOptima - AI-Powered Hospital Resource Optimization Dashboard
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from forecasting import PatientForecaster, MultiMetricForecaster
from bed_optimizer import BedOptimizer
from staff_optimizer import StaffOptimizer
from anomaly_detector import AnomalyDetector
from insight_generator import InsightGenerator
from data_generator import generate_hospital_data

# Page Configuration
st.set_page_config(
    page_title="MediOptima | Hospital Resource Optimization",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5a6c7d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-card.alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
    }
    .kpi-card.warning {
        background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
        color: #2d3436;
    }
    .kpi-card.success {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .critical { background-color: #ffebee; border-left: 4px solid #c62828; }
    .high { background-color: #fff3e0; border-left: 4px solid #ef6c00; }
    .medium { background-color: #fffde7; border-left: 4px solid #f9a825; }
    .info { background-color: #e3f2fd; border-left: 4px solid #1565c0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'models_fitted' not in st.session_state:
    st.session_state.models_fitted = False

@st.cache_data
def load_or_generate_data():
    """Load or generate hospital data."""
    try:
        # Try to load existing data
        df = pd.read_csv('hospital_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except:
        # Generate new data
        df = generate_hospital_data()
        df.to_csv('hospital_data.csv', index=False)
        return df

@st.cache_resource
def initialize_models():
    """Initialize and fit all models."""
    return {
        'forecaster': MultiMetricForecaster(),
        'bed_optimizer': BedOptimizer(),
        'staff_optimizer': StaffOptimizer(),
        'anomaly_detector': AnomalyDetector(),
        'insight_generator': InsightGenerator()
    }

def render_header():
    """Render application header."""
    st.markdown('<p class="main-header">🏥 MediOptima</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Hospital Resource Optimization System</p>', unsafe_allow_html=True)

def render_kpi_cards(df, forecast_data, bed_status, anomaly_status):
    """Render KPI cards."""
    
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pred_total = forecast_data.get('patients', {}).get('total_predicted', 0)
        st.markdown(f"""
            <div class="kpi-card">
                <div class="metric-value">{pred_total:,}</div>
                <div class="metric-label">Predicted Patients (7d)</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gen_util = bed_status.get('general_ward', {}).get('utilization', 0)
        card_class = 'alert' if gen_util > 90 else ('warning' if gen_util > 80 else 'success')
        st.markdown(f"""
            <div class="kpi-card {card_class}">
                <div class="metric-value">{gen_util}%</div>
                <div class="metric-label">Bed Utilization</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        icu_util = bed_status.get('icu', {}).get('utilization', 0)
        icu_class = 'alert' if icu_util > 90 else ('warning' if icu_util > 80 else 'success')
        st.markdown(f"""
            <div class="kpi-card {icu_class}">
                <div class="metric-value">{icu_util}%</div>
                <div class="metric-label">ICU Utilization</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status = anomaly_status.get('status', 'NORMAL')
        status_class = 'alert' if status == 'CRITICAL' else ('warning' if status in ['HIGH', 'ELEVATED'] else 'success')
        st.markdown(f"""
            <div class="kpi-card {status_class}">
                <div class="metric-value">{status}</div>
                <div class="metric-label">System Status</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

def render_forecast_tab(df, forecast_results, trend):
    """Render forecasting visualizations."""
    
    st.header("📈 Patient Inflow Forecast")
    
    # Get patient forecast data
    patient_forecast = forecast_results.get('patients', {})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Historical + Forecast chart
        fig = go.Figure()
        
        # Historical data (last 60 days)
        hist_data = df.tail(60)
        fig.add_trace(go.Scatter(
            x=hist_data['Date'],
            y=hist_data['Daily_Patients'],
            name='Historical',
            line=dict(color='#3498db', width=2)
        ))
        
        # Forecast
        if patient_forecast.get('dates'):
            forecast_dates = pd.to_datetime(patient_forecast['dates'])
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['predictions'],
                name='Forecast',
                line=dict(color='#e74c3c', width=3, dash='dash')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['upper_bound'],
                fill=None,
                mode='lines',
                line_color='rgba(231, 76, 60, 0)',
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['lower_bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(231, 76, 60, 0)',
                name='Confidence Interval'
            ))
        
        fig.update_layout(
            title='Patient Inflow: Historical vs 7-Day Forecast',
            xaxis_title='Date',
            yaxis_title='Number of Patients',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Forecast Summary")
        
        st.metric("Total (7 days)", f"{patient_forecast.get('total_predicted', 0):,}")
        st.metric("Daily Average", f"{patient_forecast.get('avg_daily', 0):,}")
        
        st.markdown("#### Trend Analysis")
        st.write(f"**Direction:** {trend.get('trend_direction', 'Stable')}")
        st.write(f"**Change:** {trend.get('change_percentage', 0):+.1f}%")
        
        # Emergency & ICU mini charts
        st.markdown("---")
        emergency_data = forecast_results.get('emergency', {})
        icu_data = forecast_results.get('icu', {})
        
        st.write(f"🚨 Emergency Cases (7d): **{emergency_data.get('total_predicted', 0):,}**")
        st.write(f"🏥 ICU Admissions (7d): **{icu_data.get('total_predicted', 0):,}**")
    
    # 7-Day breakdown table
    st.subheader("📅 7-Day Forecast Breakdown")
    
    if patient_forecast.get('dates'):
        forecast_table = pd.DataFrame({
            'Date': patient_forecast['dates'],
            'Predicted Patients': patient_forecast['predictions'],
            'Lower Bound': patient_forecast['lower_bound'],
            'Upper Bound': patient_forecast['upper_bound'],
            'Emergency (Est.)': emergency_data.get('predictions', [0]*7),
            'ICU (Est.)': icu_data.get('predictions', [0]*7)
        })
        st.dataframe(forecast_table, use_container_width=True, hide_index=True)

def render_bed_optimization_tab(df, models, forecast_results, bed_status):
    """Render bed optimization."""
    
    st.header("🛏️ Bed Requirement Estimation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("General Ward")
        gen = bed_status.get('general_ward', {})
        
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=gen.get('utilization', 0),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Utilization %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 70], 'color': '#d5f5e3'},
                    {'range': [70, 90], 'color': '#f9e79f'},
                    {'range': [90, 100], 'color': '#f5b7b1'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.write(f"**Total Beds:** {gen.get('total', 0)}")
        st.write(f"**Occupied:** {gen.get('occupied', 0)}")
        st.write(f"**Available:** {gen.get('available', 0)}")
    
    with col2:
        st.subheader("ICU")
        icu = bed_status.get('icu', {})
        
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=icu.get('utilization', 0),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ICU Utilization %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#e74c3c"},
                'steps': [
                    {'range': [0, 70], 'color': '#d5f5e3'},
                    {'range': [70, 85], 'color': '#f9e79f'},
                    {'range': [85, 100], 'color': '#f5b7b1'}
                ],
                'threshold': {
                    'line': {'color': "darkred", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
        
        st.write(f"**Total ICU Beds:** {icu.get('total', 0)}")
        st.write(f"**Occupied:** {icu.get('occupied', 0)}")
        st.write(f"**Available:** {icu.get('available', 0)}")
    
    # Bed requirement forecast
    st.markdown("---")
    st.subheader("📊 7-Day Bed Requirement Forecast")
    
    patient_forecast = forecast_results.get('patients', {})
    bed_forecast = models['bed_optimizer'].generate_7day_bed_forecast(
        patient_forecast,
        {'occupied_general': bed_status['general_ward']['occupied']}
    )
    
    bed_df = pd.DataFrame(bed_forecast)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=bed_df['date'],
        y=bed_df['required_beds'],
        name='Required Beds',
        marker_color='#e74c3c'
    ))
    fig3.add_trace(go.Bar(
        x=bed_df['date'],
        y=bed_df['available_beds'],
        name='Available Beds',
        marker_color='#2ecc71'
    ))
    fig3.update_layout(
        barmode='group',
        title='Bed Supply vs Demand (Next 7 Days)',
        xaxis_title='Date',
        yaxis_title='Number of Beds',
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Risk summary
    st.subheader("⚠️ Shortage Risk Assessment")
    
    for day in bed_forecast[:3]:  # Show first 3 days
        risk = day['shortage_risk']
        if risk == 'CRITICAL':
            st.error(f"**{day['date']}:** CRITICAL shortage risk - {day['predicted_patients']} patients expected, {day['required_beds']} beds needed")
        elif risk == 'HIGH':
            st.warning(f"**{day['date']}:** HIGH shortage risk - Monitor closely")
        else:
            st.success(f"**{day['date']}:** {risk} risk - Adequate capacity")

def render_staff_optimization_tab(models, forecast_results, staff_schedule):
    """Render staff optimization."""
    
    st.header("👨‍⚕️ Staff Scheduling Optimization")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Weekly Additional Cost", f"₹{staff_schedule.get('total_weekly_cost', 0):,}")
    with col2:
        avg_cost = staff_schedule.get('avg_daily_cost', 0)
        st.metric("Avg Daily Extra Cost", f"₹{avg_cost:,}")
    with col3:
        schedule = staff_schedule.get('daily_schedule', [])
        extra_days = len([d for d in schedule if d.get('extra_doctors_needed', 0) > 0])
        st.metric("Days Requiring Extra Staff", extra_days)
    
    # Staff schedule table
    st.markdown("---")
    st.subheader("📋 7-Day Optimized Schedule")
    
    if schedule:
        schedule_df = pd.DataFrame(schedule)
        display_df = schedule_df[[
            'date', 'predicted_patients', 'predicted_icu',
            'min_doctors_required', 'min_nurses_required', 'min_icu_nurses_required',
            'extra_doctors_needed', 'extra_nurses_needed', 'extra_icu_nurses_needed',
            'additional_cost'
        ]]
        display_df.columns = [
            'Date', 'Pred. Patients', 'Pred. ICU',
            'Req. Doctors', 'Req. Nurses', 'Req. ICU Nurses',
            'Extra Doctors', 'Extra Nurses', 'Extra ICU Nurses',
            'Add. Cost (₹)'
        ]
        
        # Color code based on extra staff needs
        def highlight_extra(row):
            styles = [''] * len(row)
            if row['Extra Doctors'] > 0 or row['Extra Nurses'] > 0:
                styles = ['background-color: #ffebee'] * len(row)
            return styles
        
        st.dataframe(
            display_df.style.apply(highlight_extra, axis=1),
            use_container_width=True,
            hide_index=True
        )
    
    # Staffing ratios visualization
    st.markdown("---")
    st.subheader("📊 Staff-to-Patient Ratios")
    
    if schedule:
        schedule_df = pd.DataFrame(schedule)
        
        fig = make_subplots(rows=1, cols=3, subplot_titles=['Doctors', 'Nurses', 'ICU Nurses'])
        
        # Doctor ratio
        doctor_ratio = schedule_df['min_doctors_required'] / schedule_df['predicted_patients']
        fig.add_trace(go.Scatter(
            x=schedule_df['date'], y=doctor_ratio,
            mode='lines+markers', name='Doctor Ratio',
            line=dict(color='#3498db')
        ), row=1, col=1)
        fig.add_hline(y=1/20, line_dash="dash", line_color="red", row=1, col=1)
        
        # Nurse ratio
        nurse_ratio = schedule_df['min_nurses_required'] / schedule_df['predicted_patients']
        fig.add_trace(go.Scatter(
            x=schedule_df['date'], y=nurse_ratio,
            mode='lines+markers', name='Nurse Ratio',
            line=dict(color='#2ecc71')
        ), row=1, col=2)
        fig.add_hline(y=1/8, line_dash="dash", line_color="red", row=1, col=2)
        
        # ICU ratio
        icu_ratio = schedule_df['min_icu_nurses_required'] / schedule_df['predicted_icu']
        fig.add_trace(go.Scatter(
            x=schedule_df['date'], y=icu_ratio,
            mode='lines+markers', name='ICU Nurse Ratio',
            line=dict(color='#e74c3c')
        ), row=1, col=3)
        fig.add_hline(y=1/2, line_dash="dash", line_color="red", row=1, col=3)
        
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Staffing Recommendations")
    
    recommendations = models['staff_optimizer'].get_staffing_recommendations(staff_schedule)
    for rec in recommendations:
        st.info(rec)

def render_anomaly_detection_tab(df, models, anomaly_status):
    """Render anomaly detection."""
    
    st.header("🚨 Surge & Anomaly Detection")
    
    # Current status
    status = anomaly_status.get('status', 'NORMAL')
    
    if status == 'CRITICAL':
        st.error(f"## 🔴 CRITICAL ALERT: Multiple system thresholds breached!")
    elif status == 'HIGH':
        st.warning(f"## 🟠 HIGH ALERT: Elevated system pressure detected")
    elif status == 'ELEVATED':
        st.info(f"## 🟡 ELEVATED: Minor threshold breach detected")
    else:
        st.success(f"## 🟢 NORMAL: All systems within normal parameters")
    
    # Latest values
    st.markdown("---")
    st.subheader("📊 Current Status")
    
    latest = anomaly_status.get('latest_values', {})
    thresholds = anomaly_status.get('thresholds', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        patients = latest.get('patients', 0)
        threshold = thresholds.get('patient_threshold', 0)
        delta = patients - threshold
        st.metric(
            "Daily Patients",
            f"{patients:,}",
            f"{delta:+d} vs 95th percentile",
            delta_color="inverse"
        )
    
    with col2:
        emergency = latest.get('emergency', 0)
        threshold = thresholds.get('emergency_threshold', 0)
        delta = emergency - threshold
        st.metric(
            "Emergency Cases",
            f"{emergency:,}",
            f"{delta:+d} vs 95th percentile",
            delta_color="inverse"
        )
    
    with col3:
        icu = latest.get('icu', 0)
        threshold = thresholds.get('icu_threshold', 0)
        delta = icu - threshold
        st.metric(
            "ICU Admissions",
            f"{icu:,}",
            f"{delta:+d} vs 95th percentile",
            delta_color="inverse"
        )
    
    # Historical anomalies
    st.markdown("---")
    st.subheader("📈 Historical Anomaly Detection")
    
    # Detect anomalies
    z_anomalies = models['anomaly_detector'].detect_zscore_anomalies(df)
    iso_anomalies = models['anomaly_detector'].detect_isolation_anomalies(df)
    surge_periods = models['anomaly_detector'].detect_surge_pattern(df)
    
    # Plot with anomalies highlighted
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Daily_Patients'],
        name='Daily Patients',
        line=dict(color='#3498db', width=2)
    ))
    
    # Highlight Z-score anomalies
    if not z_anomalies.empty:
        fig.add_trace(go.Scatter(
            x=z_anomalies['Date'],
            y=z_anomalies['Daily_Patients'],
            mode='markers',
            name='Z-Score Anomalies',
            marker=dict(color='#e74c3c', size=12, symbol='x')
        ))
    
    fig.update_layout(
        title='Patient Flow with Anomaly Detection',
        xaxis_title='Date',
        yaxis_title='Patients',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Surge periods table
    if surge_periods:
        st.subheader("⚡ Detected Surge Periods")
        surge_df = pd.DataFrame(surge_periods)
        st.dataframe(surge_df, use_container_width=True, hide_index=True)
    
    # Anomaly statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Z-Score Anomalies (All Time)", len(z_anomalies))
    with col2:
        st.metric("Isolation Forest Anomalies", len(iso_anomalies))

def render_insights_tab(insights):
    """Render AI insights."""
    
    st.header("🤖 AI-Generated Insights")
    
    # Forecast summary
    st.markdown(insights.get('forecast_summary', 'No forecast summary available'))
    
    # Resource alerts
    st.markdown("---")
    st.subheader("⚠️ Resource Alerts")
    
    alerts = insights.get('resource_alerts', [])
    for alert in alerts:
        level = alert.get('level', 'INFO')
        if level == 'CRITICAL':
            st.error(f"**{alert.get('type', 'Alert')}:** {alert.get('message', '')}")
        elif level == 'WARNING':
            st.warning(f"**{alert.get('type', 'Alert')}:** {alert.get('message', '')}")
        else:
            st.info(f"**{alert.get('type', 'Alert')}:** {alert.get('message', '')}")
    
    # Action items
    st.markdown("---")
    st.subheader("✅ Priority Action Items")
    
    actions = insights.get('action_items', [])
    
    priority_colors = {1: '🔴', 2: '🟡', 3: '🟢'}
    
    for action in actions:
        priority = action.get('priority', 3)
        color = priority_colors.get(priority, '⚪')
        
        with st.expander(f"{color} Priority {priority}: {action.get('action', 'No action')}"):
            st.write(f"**Owner:** {action.get('owner', 'Unassigned')}")
            st.write(f"**Deadline:** {action.get('deadline', 'Not set')}")

def main():
    """Main application."""
    
    render_header()
    
    # Load data
    df = load_or_generate_data()
    
    # Initialize models
    models = initialize_models()
    
    # Fit models if not already done
    if not st.session_state.models_fitted:
        with st.spinner('Initializing AI models... This may take a moment.'):
            # Fit forecasters
            raw_results = models['forecaster'].fit_all(df, periods=30)
            
            # Get properly mapped forecast results
            forecast_results = models['forecaster'].get_combined_forecast()
            
            # Fit anomaly detector
            models['anomaly_detector'].fit_baseline(df)
            
            st.session_state.models_fitted = True
            st.session_state.forecast_results = forecast_results
    
    # Get cached results
    forecast_results = st.session_state.forecast_results
    
    # Get additional analyses
    trend = models['forecaster'].forecasters['Daily_Patients'].get_trend_analysis()
    bed_status = models['bed_optimizer'].get_capacity_summary(df, 
        models['forecaster'].forecasters['Daily_Patients'].forecast_df)
    
    # Get staff schedule
    base_staffing = {
        'doctors': int(df['Doctors_On_Duty'].mean()),
        'nurses': int(df['Nurses_On_Duty'].mean()),
        'icu_nurses': int(df['ICU_Nurses'].mean())
    }
    staff_schedule = models['staff_optimizer'].generate_weekly_schedule(
        forecast_results['patients'],
        forecast_results['icu'],
        base_staffing
    )
    
    # Get anomaly status
    anomaly_status = models['anomaly_detector'].get_current_status(df)
    
    # Generate insights
    insights = models['insight_generator'].generate_all_insights(
        forecast_results, trend, bed_status, staff_schedule, anomaly_status
    )
    
    # Render KPI cards
    render_kpi_cards(df, forecast_results, bed_status, anomaly_status)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Forecast", "🛏️ Bed Optimization", "👨‍⚕️ Staff Optimization", 
        "🚨 Anomaly Detection", "🤖 AI Insights"
    ])
    
    with tab1:
        render_forecast_tab(df, forecast_results, trend)
    
    with tab2:
        render_bed_optimization_tab(df, models, forecast_results, bed_status)
    
    with tab3:
        render_staff_optimization_tab(models, forecast_results, staff_schedule)
    
    with tab4:
        render_anomaly_detection_tab(df, models, anomaly_status)
    
    with tab5:
        render_insights_tab(insights)
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>MediOptima © 2024 | AI-Powered Hospital Resource Optimization</p>", 
                unsafe_allow_html=True)

if __name__ == '__main__':
    main()
