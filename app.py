"""
MediOptima - AI-Powered Hospital Resource Optimization Dashboard
Professional Healthcare Management System
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import time
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from forecasting import PatientForecaster, MultiMetricForecaster
from bed_optimizer import BedOptimizer
from staff_optimizer import StaffOptimizer
from anomaly_detector import AnomalyDetector
from insight_generator import InsightGenerator
from data_generator import generate_hospital_data
from data_manager import HospitalDataManager

# Page Configuration
st.set_page_config(
    page_title="MediOptima | Hospital Resource Optimization",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Akashkumar37443/MediOptima',
        'Report a bug': 'https://github.com/Akashkumar37443/MediOptima/issues',
        'About': '# MediOptima\nAI-Powered Hospital Resource Optimization System'
    }
)

# Professional Healthcare Theme
st.markdown("""
<style>
    /* Clean professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Light clean background - healthcare professional */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        color: #334155;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main header - clean medical style */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 8px;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* KPI Cards - Clean medical cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .kpi-card.alert {
        background: #fef2f2;
        border: 1px solid #fecaca;
    }
    
    .kpi-card.warning {
        background: #fffbeb;
        border: 1px solid #fde68a;
    }
    
    .kpi-card.success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Section headers - Clean medical style */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1e40af;
        font-weight: 600;
    }
    
    h2 {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-bottom: 20px;
        color: #1e40af;
    }
    
    /* Tab styling - Clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #ffffff;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        padding: 10px 20px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #64748b;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        color: #1e40af;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1e40af !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Alert boxes - Clean medical style */
    .alert-box {
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left-width: 4px;
    }
    
    .critical { 
        background: #fef2f2; 
        border-left-color: #dc2626;
        color: #991b1b;
    }
    
    .high { 
        background: #fffbeb; 
        border-left-color: #f59e0b;
        color: #92400e;
    }
    
    .medium { 
        background: #fefce8; 
        border-left-color: #eab308;
        color: #854d0e;
    }
    
    .info { 
        background: #eff6ff; 
        border-left-color: #3b82f6;
        color: #1e40af;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Button styling - Clean medical */
    .stButton > button {
        background: #1e40af;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1e3a8a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: #1e40af;
        border-radius: 4px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #1e40af transparent !important;
    }
    
    /* Widget labels */
    .css-1vbkxwb {
        color: #475569 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        color: #334155;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background: #ffffff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e2e8f0;
    }
    
    [data-testid="metric-container"] label {
        color: #64748b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500;
    }
    
    [data-testid="metric-container"] div {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'models_fitted' not in st.session_state:
    st.session_state.models_fitted = False

@st.cache_data
def load_or_generate_data():
    """Load data from cache or generate synthetic data."""
    # Try to load cached CSV
    try:
        df = pd.read_csv('hospital_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except:
        # Generate synthetic data
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
    """Render clean professional header."""
    # Simple clean medical logo
    st.markdown("""
        <div style="text-align: center; margin-bottom: 16px;">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 64px;
                height: 64px;
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 16px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
            ">
                <span style="font-size: 32px; color: white;">🏥</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-header">MediOptima</p>', unsafe_allow_html=True)
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
        # Historical + Forecast chart with futuristic theme
        fig = go.Figure()
        
        # Historical data (last 60 days)
        hist_data = df.tail(60)
        fig.add_trace(go.Scatter(
            x=hist_data['Date'],
            y=hist_data['Daily_Patients'],
            name='Historical',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        # Forecast
        if patient_forecast.get('dates'):
            forecast_dates = pd.to_datetime(patient_forecast['dates'])
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['predictions'],
                name='Forecast',
                line=dict(color='#1e40af', width=3),
                mode='lines+markers',
                marker=dict(size=6, color='#1e40af')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['upper_bound'],
                fill=None,
                mode='lines',
                line_color='rgba(30, 64, 175, 0)',
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['lower_bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(30, 64, 175, 0)',
                fillcolor='rgba(30, 64, 175, 0.15)',
                name='Confidence Interval'
            ))
        
        fig.update_layout(
            title=dict(
                text='Patient Inflow Forecast',
                font=dict(family='Inter', size=16, color='#1e293b'),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#f8fafc',
            xaxis=dict(
                title=dict(text='Date', font=dict(color='#475569', family='Inter')),
                gridcolor='#e2e8f0',
                linecolor='#cbd5e1',
                tickfont=dict(color='#64748b', family='Inter')
            ),
            yaxis=dict(
                title=dict(text='Number of Patients', font=dict(color='#475569', family='Inter')),
                gridcolor='#e2e8f0',
                linecolor='#cbd5e1',
                tickfont=dict(color='#64748b', family='Inter')
            ),
            height=400,
            hovermode='x unified',
            legend=dict(
                font=dict(family='Inter', color='#475569'),
                bgcolor='#ffffff',
                bordercolor='#e2e8f0',
                borderwidth=1
            ),
            margin=dict(l=60, r=30, t=60, b=60)
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
            title={'text': "Utilization %", 'font': {'size': 16}},
            number={'font': {'size': 40, 'color': '#2c3e50'}, 'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3498db", 'thickness': 0.6},
                'bgcolor': 'white',
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
        fig1.update_layout(height=350, margin=dict(t=50, b=30))
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
            title={'text': "ICU Utilization %", 'font': {'size': 16}},
            number={'font': {'size': 40, 'color': '#2c3e50'}, 'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#e74c3c", 'thickness': 0.6},
                'bgcolor': 'white',
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
        fig2.update_layout(height=350, margin=dict(t=50, b=30))
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

def render_patient_management_tab(data_manager):
    """Render interactive patient management."""
    st.header("👤 Patient Management")
    
    # Initialize session state variables if not exists
    if 'discharges_today' not in st.session_state:
        st.session_state.discharges_today = 0
    if 'admissions_today' not in st.session_state:
        st.session_state.admissions_today = 0
    
    # Quick stats
    patients = st.session_state.patients
    active_patients = patients[patients['status'] == 'Active']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Patients", len(active_patients))
    col2.metric("Critical", len(patients[patients['status'] == 'Critical']))
    col3.metric("Recovering", len(patients[patients['status'] == 'Recovering']))
    col4.metric("Discharged Today", st.session_state.discharges_today)
    
    # Admit new patient
    st.subheader("➕ Admit New Patient")
    with st.form("admit_patient"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 1, 120, 45)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        with col2:
            condition = st.selectbox("Condition", [
                'Flu', 'Pneumonia', 'Heart Disease', 'Diabetes', 'Hypertension', 
                'Asthma', 'COVID-19', 'Fracture', 'Stroke', 'Cancer', 'Other'
            ])
            ward = st.selectbox("Ward", ['General', 'ICU', 'Emergency', 'Surgery', 'Maternity', 'Pediatrics', 'Cardiology'])
            insurance = st.selectbox("Insurance", ['Private', 'Medicare', 'Medicaid', 'Self-Pay'])
        
        with col3:
            # Show available beds
            available_beds = data_manager.get_available_beds(ward if ward != 'Emergency' else None)
            if not available_beds.empty:
                bed_options = available_beds['bed_id'].tolist()
                bed = st.selectbox("Assign Bed", bed_options)
            else:
                st.error("No beds available!")
                bed = None
            
            doctor = st.text_input("Assigned Doctor", "Dr. Smith")
        
        submitted = st.form_submit_button("Admit Patient", type="primary")
        
        if submitted and name and bed:
            new_patient = {
                'patient_id': f'P{10000 + len(patients)}',
                'name': name,
                'age': age,
                'gender': gender,
                'condition': condition,
                'ward': ward,
                'status': 'Active',
                'admission_date': datetime.now(),
                'bed_number': bed,
                'doctor': doctor,
                'insurance': insurance,
                'contact': '+1-555-0000',
                'emergency_contact': '+1-555-0000'
            }
            
            data_manager.admit_patient(new_patient)
            data_manager.assign_bed(bed, new_patient['patient_id'])
            st.success(f"✅ Patient {name} admitted successfully! ID: {new_patient['patient_id']}")
            st.rerun()
    
    # Patient list with actions
    st.subheader("📋 Patient List")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("🔍 Search by Name", "", placeholder="Type patient name...")
    with col2:
        status_filter = st.selectbox("Filter by Status", ['All', 'Active', 'Critical', 'Stable', 'Recovering', 'Discharged'])
    with col3:
        ward_filter = st.selectbox("Filter by Ward", ['All'] + patients['ward'].unique().tolist())
    
    filtered_patients = patients.copy()
    
    # Sort by admission date - newest first
    filtered_patients['admission_date'] = pd.to_datetime(filtered_patients['admission_date'])
    filtered_patients = filtered_patients.sort_values('admission_date', ascending=False)
    
    # Apply filters
    if search_name:
        filtered_patients = filtered_patients[filtered_patients['name'].str.contains(search_name, case=False, na=False)]
    if status_filter != 'All':
        filtered_patients = filtered_patients[filtered_patients['status'] == status_filter]
    if ward_filter != 'All':
        filtered_patients = filtered_patients[filtered_patients['ward'] == ward_filter]
    
    st.write(f"**Showing {len(filtered_patients)} patients** (Newest first)")
    
    # Display patients with action buttons
    for idx, patient in filtered_patients.head(20).iterrows():
        with st.expander(f"{patient['name']} | {patient['condition']} | {patient['status']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**ID:** {patient['patient_id']}")
                st.write(f"**Age:** {patient['age']} | **Gender:** {patient['gender']}")
                st.write(f"**Ward:** {patient['ward']} | **Bed:** {patient['bed_number']}")
            
            with col2:
                st.write(f"**Doctor:** {patient['doctor']}")
                st.write(f"**Insurance:** {patient['insurance']}")
                st.write(f"**Admitted:** {patient['admission_date']}")
            
            with col3:
                if patient['status'] != 'Discharged':
                    if st.button("Discharge", key=f"discharge_{patient['patient_id']}"):
                        data_manager.discharge_patient(patient['patient_id'])
                        st.success(f"✅ {patient['name']} discharged!")
                        st.rerun()
                    
                    if st.button("Transfer", key=f"transfer_{patient['patient_id']}"):
                        st.session_state[f"transfer_mode_{patient['patient_id']}"] = True
                    
                    if st.session_state.get(f"transfer_mode_{patient['patient_id']}", False):
                        new_ward = st.selectbox("New Ward", ['General', 'ICU', 'Emergency', 'Surgery'], key=f"ward_{patient['patient_id']}")
                        avail_beds = data_manager.get_available_beds(new_ward)
                        if not avail_beds.empty:
                            new_bed = st.selectbox("New Bed", avail_beds['bed_id'].tolist(), key=f"bed_{patient['patient_id']}")
                            if st.button("Confirm Transfer", key=f"confirm_{patient['patient_id']}"):
                                data_manager.transfer_patient(patient['patient_id'], new_ward, new_bed)
                                st.success(f"✅ {patient['name']} transferred to {new_ward}!")
                                st.rerun()

def render_bed_management_tab(data_manager):
    """Render interactive bed management."""
    st.header("🛏️ Bed Management")
    
    beds = st.session_state.beds
    
    # Overview
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", len(beds))
    col2.metric("Occupied", len(beds[beds['status'] == 'Occupied']))
    col3.metric("Available", len(beds[beds['status'] == 'Available']))
    col4.metric("Maintenance", len(beds[beds['status'] == 'Maintenance']))
    col5.metric("Reserved", len(beds[beds['status'] == 'Reserved']))
    
    # Ward breakdown
    st.subheader("📊 Ward Status")
    ward_summary = beds.groupby('ward')['status'].value_counts().unstack(fill_value=0)
    st.bar_chart(ward_summary)
    
    # Bed list with status updates
    st.subheader("🛏️ Bed Details")
    
    ward_filter = st.selectbox("Select Ward", ['All'] + beds['ward'].unique().tolist())
    filtered_beds = beds if ward_filter == 'All' else beds[beds['ward'] == ward_filter]
    
    # Show beds in a grid
    bed_cols = st.columns(5)
    for idx, bed in filtered_beds.iterrows():
        with bed_cols[idx % 5]:
            status_color = {
                'Available': '🟢',
                'Occupied': '🔴',
                'Maintenance': '🟡',
                'Reserved': '🔵'
            }.get(bed['status'], '⚪')
            
            st.write(f"{status_color} **{bed['bed_id']}**")
            st.caption(f"{bed['ward']} | {bed['status']}")
            
            if bed['status'] == 'Maintenance':
                if st.button("Complete Repair", key=f"repair_{bed['bed_id']}"):
                    data_manager.release_bed(bed['bed_id'])
                    st.rerun()
            elif bed['status'] == 'Available':
                if st.button("Set Maintenance", key=f"maint_{bed['bed_id']}"):
                    beds.loc[beds['bed_id'] == bed['bed_id'], 'status'] = 'Maintenance'
                    st.session_state.beds = beds
                    st.rerun()

def render_staff_management_tab(data_manager):
    """Render interactive staff management."""
    st.header("👨‍⚕️ Staff Management")
    
    staff = st.session_state.staff
    
    # Overview
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("On Duty", len(staff[staff['status'] == 'On Duty']))
    col2.metric("Off Duty", len(staff[staff['status'] == 'Off Duty']))
    col3.metric("On Leave", len(staff[staff['status'] == 'On Leave']))
    col4.metric("Busy", len(staff[staff['status'] == 'Busy']))
    
    # Role breakdown
    st.subheader("📊 Staff by Role")
    role_counts = staff['role'].value_counts()
    st.bar_chart(role_counts)
    
    # Staff list with status updates
    st.subheader("👥 Staff Roster")
    
    role_filter = st.selectbox("Filter by Role", ['All'] + staff['role'].unique().tolist())
    filtered_staff = staff if role_filter == 'All' else staff[staff['role'] == role_filter]
    
    # Show staff with status toggle
    for idx, member in filtered_staff.iterrows():
        with st.expander(f"{member['name']} | {member['role']} | {member['status']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**ID:** {member['staff_id']}")
                st.write(f"**Department:** {member['department']}")
                st.write(f"**Shift:** {member['shift']}")
            
            with col2:
                st.write(f"**Phone:** {member['phone']}")
                st.write(f"**Email:** {member['email']}")
                if member['role'] in ['Doctor', 'Nurse']:
                    st.write(f"**Patients:** {member['patients_assigned']}")
            
            with col3:
                new_status = st.selectbox(
                    "Update Status",
                    ['On Duty', 'Off Duty', 'On Leave', 'Busy'],
                    index=['On Duty', 'Off Duty', 'On Leave', 'Busy'].index(member['status']),
                    key=f"status_{member['staff_id']}"
                )
                
                if new_status != member['status']:
                    if st.button("Update", key=f"update_{member['staff_id']}"):
                        data_manager.update_staff_status(member['staff_id'], new_status)
                        st.success(f"✅ Status updated to {new_status}!")
                        st.rerun()

def render_equipment_management_tab(data_manager):
    """Render interactive equipment management."""
    st.header("🔧 Equipment & Resources")
    
    equipment = st.session_state.equipment
    
    # Overview
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Available", len(equipment[equipment['status'] == 'Available']))
    col2.metric("In Use", len(equipment[equipment['status'] == 'In Use']))
    col3.metric("Maintenance", len(equipment[equipment['status'] == 'Maintenance']))
    col4.metric("Out of Order", len(equipment[equipment['status'] == 'Out of Order']))
    
    # Equipment by type
    st.subheader("📊 Equipment by Type")
    type_status = equipment.groupby('type')['status'].value_counts().unstack(fill_value=0)
    st.bar_chart(type_status)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Use Equipment**")
        eq_type = st.selectbox("Equipment Type", equipment['type'].unique().tolist(), key="use_eq_type")
        available_eq = data_manager.get_available_equipment(eq_type)
        
        if not available_eq.empty:
            eq_to_use = st.selectbox("Select Equipment", available_eq['equipment_id'].tolist(), key="use_eq")
            patient_for_eq = st.text_input("Patient ID (optional)", "", key="eq_patient")
            
            if st.button("Mark In Use", type="primary"):
                data_manager.use_equipment(eq_to_use, patient_for_eq if patient_for_eq else None)
                st.success(f"✅ Equipment {eq_to_use} marked as In Use!")
                st.rerun()
        else:
            st.warning("No available equipment of this type")
    
    with col2:
        st.write("**Return Equipment**")
        in_use_eq = equipment[equipment['status'] == 'In Use']
        
        if not in_use_eq.empty:
            eq_to_return = st.selectbox("Select Equipment", in_use_eq['equipment_id'].tolist(), key="return_eq")
            
            if st.button("Mark Available"):
                data_manager.update_equipment_status(eq_to_return, 'Available')
                st.success(f"✅ Equipment {eq_to_return} returned!")
                st.rerun()
        else:
            st.info("No equipment currently in use")
    
    # Equipment list
    st.subheader("🔧 Equipment Inventory")
    
    type_filter = st.selectbox("Filter by Type", ['All'] + equipment['type'].unique().tolist())
    filtered_equipment = equipment if type_filter == 'All' else equipment[equipment['type'] == type_filter]
    
    st.dataframe(filtered_equipment[['equipment_id', 'name', 'type', 'status', 'location', 'condition']], 
                 use_container_width=True)

def main():
    """Main application."""
    
    # Sidebar - Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        forecast_days = st.slider("Forecast Days", 7, 30, 7)
        
        st.markdown("---")
        st.markdown("**Need Help?**")
        st.markdown("[Documentation](https://github.com/Akashkumar37443/MediOptima)")
    
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
    
    # Initialize data manager for interactive features
    data_manager = HospitalDataManager()
    
    # Real-time stats
    live_stats = data_manager.get_current_stats()
    
    # Live metrics display
    st.markdown("---")
    st.subheader("📊 Live Hospital Status")
    
    stat_col1, stat_col2, stat_col3, stat_col4, stat_col5, stat_col6 = st.columns(6)
    
    with stat_col1:
        st.metric("🛏️ Beds Occupied", 
                 f"{live_stats['occupied_beds']}/{live_stats['total_beds']}",
                 f"{live_stats['available_beds']} available")
    
    with stat_col2:
        st.metric("👥 Active Patients", live_stats['total_patients'])
    
    with stat_col3:
        st.metric("⚠️ Critical", live_stats['critical_patients'])
    
    with stat_col4:
        st.metric("👨‍⚕️ Staff On Duty", 
                 f"{live_stats['staff_on_duty']}/{live_stats['total_staff']}")
    
    with stat_col5:
        st.metric("🔧 Equipment In Use", 
                 f"{live_stats['equipment_in_use']}/{live_stats['equipment_available'] + live_stats['equipment_in_use']}")
    
    with stat_col6:
        st.metric("📈 Today's Admissions", 
                 live_stats['admissions_today'],
                 f"{live_stats['discharges_today']} discharges")
    
    st.markdown("---")
    
    # Main Navigation Tabs - Extended with interactive features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Forecast", "🛏️ Bed Planning", "👨‍⚕️ Staff Scheduling", 
        "⚠️ Alerts", "💡 Insights", "👤 Patients", "🛏️ Bed Mgmt", 
        "👨‍⚕️ Staff Mgmt", "🔧 Equipment"
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
    
    with tab6:
        render_patient_management_tab(data_manager)
    
    with tab7:
        render_bed_management_tab(data_manager)
    
    with tab8:
        render_staff_management_tab(data_manager)
    
    with tab9:
        render_equipment_management_tab(data_manager)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="
            text-align: center; 
            padding: 20px;
            margin-top: 30px;
            color: #64748b;
            font-size: 0.9rem;
        ">
            <strong style="color: #1e40af;">MediOptima</strong> | 
            Hospital Resource Optimization System | 
            Built with Streamlit
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
