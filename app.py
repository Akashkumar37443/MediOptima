"""
🚀 MediOptima - AI-Powered Hospital Resource Optimization Dashboard
Futuristic Healthcare Analytics Platform
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

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from forecasting import PatientForecaster, MultiMetricForecaster
from bed_optimizer import BedOptimizer
from staff_optimizer import StaffOptimizer
from anomaly_detector import AnomalyDetector
from insight_generator import InsightGenerator
from data_generator import generate_hospital_data

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    PAGE CONFIGURATION - FUTURISTIC THEME                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="⚕️ MediOptima | Neural Healthcare OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/Akashkumar37443/MediOptima',
        'Report a bug': 'https://github.com/Akashkumar37443/MediOptima/issues',
        'About': '# MediOptima v2.0\nAI-Powered Hospital Resource Optimization'
    }
)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    CYBERPUNK / FUTURISTIC CSS THEME                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
    /* Import futuristic fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* Global dark theme with animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e, #16213e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism card effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 150, 255, 0.2);
        border: 1px solid rgba(0, 200, 255, 0.3);
    }
    
    /* Neon glow effects */
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        text-shadow: 
            0 0 5px #00d4ff,
            0 0 10px #00d4ff,
            0 0 20px #00d4ff,
            0 0 40px #00d4ff;
        color: #fff;
        letter-spacing: 2px;
    }
    
    .neon-pulse {
        animation: neonPulse 2s ease-in-out infinite;
    }
    
    @keyframes neonPulse {
        0%, 100% { opacity: 1; text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
        50% { opacity: 0.8; text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff; }
    }
    
    /* Main header styling */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf, #00d4ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        animation: shimmer 3s linear infinite;
        letter-spacing: 4px;
        margin-bottom: 10px;
    }
    
    @keyframes shimmer {
        to { background-position: 200% center; }
    }
    
    .sub-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.3rem;
        color: #8892b0;
        text-align: center;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 40px;
    }
    
    /* KPI Cards - Holographic effect */
    .kpi-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 44, 191, 0.1) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 25px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00d4ff, #7b2cbf, #00d4ff);
        border-radius: 16px;
        opacity: 0;
        z-index: -1;
        transition: opacity 0.3s ease;
    }
    
    .kpi-card:hover::before {
        opacity: 0.5;
    }
    
    .kpi-card.alert {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(153, 27, 27, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.5);
        animation: alertPulse 2s ease-in-out infinite;
    }
    
    @keyframes alertPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.6); }
    }
    
    .kpi-card.warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(180, 83, 9, 0.15) 100%);
        border: 1px solid rgba(245, 158, 11, 0.5);
    }
    
    .kpi-card.success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 95, 70, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #fff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background: rgba(0, 0, 0, 0.2);
        padding: 10px;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 12px 24px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        color: #8892b0;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(123, 44, 191, 0.2) 100%) !important;
        color: #00d4ff !important;
        border: 1px solid rgba(0, 212, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Alert boxes */
    .alert-box {
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid;
        position: relative;
        overflow: hidden;
    }
    
    .alert-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
        animation: scan 3s ease infinite;
    }
    
    @keyframes scan {
        100% { transform: translateX(100%); }
    }
    
    .critical { 
        background: rgba(239, 68, 68, 0.1); 
        border-left-color: #ef4444;
        color: #fca5a5;
    }
    
    .high { 
        background: rgba(245, 158, 11, 0.1); 
        border-left-color: #f59e0b;
        color: #fcd34d;
    }
    
    .medium { 
        background: rgba(234, 179, 8, 0.1); 
        border-left-color: #eab308;
        color: #fde047;
    }
    
    .info { 
        background: rgba(59, 130, 246, 0.1); 
        border-left-color: #3b82f6;
        color: #93c5fd;
    }
    
    /* Section headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        letter-spacing: 2px;
    }
    
    h2 {
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.5);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        border-radius: 10px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff, #7b2cbf);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00e4ff, #8b3cdf);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #00d4ff transparent !important;
    }
    
    /* Widget labels */
    .css-1vbkxwb {
        color: #8892b0 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        color: #fff;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    [data-testid="metric-container"] label {
        color: #8892b0 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    [data-testid="metric-container"] div {
        color: #00d4ff !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    
    /* Floating particles effect */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
</style>

<!-- Animated particles overlay -->
<div class="particles">
    <canvas id="particles-canvas"></canvas>
</div>

<script>
    // Simple particle animation
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const particles = [];
        for (let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2
            });
        }
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 212, 255, 0.3)';
                ctx.fill();
            });
            requestAnimationFrame(animate);
        }
        animate();
    }
</script>
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
    """Render futuristic application header."""
    # Animated neural network logo effect
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <svg width="120" height="120" viewBox="0 0 120 120" style="animation: rotate 10s linear infinite;">
                <defs>
                    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#7b2cbf;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <circle cx="60" cy="60" r="50" fill="none" stroke="url(#grad1)" stroke-width="2" opacity="0.3"/>
                <circle cx="60" cy="60" r="40" fill="none" stroke="url(#grad1)" stroke-width="2" opacity="0.5">
                    <animate attributeName="r" values="40;45;40" dur="3s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="60" r="30" fill="none" stroke="url(#grad1)" stroke-width="3"/>
                <text x="60" y="68" text-anchor="middle" fill="url(#grad1)" font-size="30" font-family="Orbitron">⚕</text>
            </svg>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-header">MEDIOPTIMA</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">NEURAL HEALTHCARE RESOURCE OPTIMIZATION SYSTEM v2.0</p>', unsafe_allow_html=True)
    
    # Live status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <span style="
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    background: #00d4ff;
                    border-radius: 50%;
                    animation: pulse 2s ease-in-out infinite;
                    box-shadow: 0 0 10px #00d4ff;
                    margin-right: 10px;
                "></span>
                <span style="color: #00d4ff; font-family: 'Rajdhani', sans-serif; letter-spacing: 3px;">
                    SYSTEM ONLINE ● AI ENGINE ACTIVE
                </span>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(1.2); }
                }
                @keyframes rotate {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        """, unsafe_allow_html=True)

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
            name='◈ HISTORICAL',
            line=dict(color='#00d4ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        
        # Forecast
        if patient_forecast.get('dates'):
            forecast_dates = pd.to_datetime(patient_forecast['dates'])
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['predictions'],
                name='◉ NEURAL FORECAST',
                line=dict(color='#7b2cbf', width=3, dash='solid'),
                mode='lines+markers',
                marker=dict(size=8, color='#7b2cbf', line=dict(color='#00d4ff', width=2))
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['upper_bound'],
                fill=None,
                mode='lines',
                line_color='rgba(123, 44, 191, 0)',
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=patient_forecast['lower_bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(123, 44, 191, 0)',
                fillcolor='rgba(123, 44, 191, 0.2)',
                name='◊ CONFIDENCE ZONE'
            ))
        
        fig.update_layout(
            title=dict(
                text='<b>◈ PATIENT INFLOW PREDICTION MODEL</b>',
                font=dict(family='Orbitron', size=18, color='#00d4ff'),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.3)',
            xaxis=dict(
                title='TEMPORAL AXIS',
                gridcolor='rgba(0, 212, 255, 0.2)',
                linecolor='rgba(0, 212, 255, 0.5)',
                tickfont=dict(color='#8892b0', family='Rajdhani'),
                titlefont=dict(color='#00d4ff', family='Orbitron')
            ),
            yaxis=dict(
                title='PATIENT COUNT',
                gridcolor='rgba(0, 212, 255, 0.2)',
                linecolor='rgba(0, 212, 255, 0.5)',
                tickfont=dict(color='#8892b0', family='Rajdhani'),
                titlefont=dict(color='#00d4ff', family='Orbitron')
            ),
            height=450,
            hovermode='x unified',
            legend=dict(
                font=dict(family='Rajdhani', color='#8892b0'),
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(0, 212, 255, 0.3)',
                borderwidth=1
            ),
            margin=dict(l=60, r=30, t=80, b=60)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
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
    
    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                    NEURAL INTERFACE TABS                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "◈ PREDICTION ENGINE", "◉ RESOURCE MATRIX", "◊ OPTIMIZATION CORE", 
        "⚡ ANOMALY DETECTOR", "◆ NEURAL INSIGHTS"
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
    
    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                    SYSTEM FOOTER - CYBERPUNK STYLE                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    st.markdown("""
        <div style="
            text-align: center; 
            padding: 30px 20px; 
            margin-top: 50px;
            background: linear-gradient(180deg, transparent, rgba(0,212,255,0.05));
            border-top: 1px solid rgba(0,212,255,0.2);
        ">
            <div style="
                font-family: 'Orbitron', sans-serif;
                font-size: 1.2rem;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: 4px;
                margin-bottom: 10px;
            ">
                ◈ MEDIOPTIMA NEURAL SYSTEM v2.0 ◈
            </div>
            <div style="
                font-family: 'Rajdhani', sans-serif;
                color: #8892b0;
                font-size: 0.9rem;
                letter-spacing: 2px;
            ">
                QUANTUM HEALTHCARE ANALYTICS ● AI-POWERED RESOURCE OPTIMIZATION
            </div>
            <div style="
                margin-top: 15px;
                font-family: 'Rajdhani', sans-serif;
                color: #00d4ff;
                font-size: 0.8rem;
                opacity: 0.7;
            ">
                ◊ Built with Streamlit ● Powered by Neural Networks ◊
            </div>
            <div style="margin-top: 20px;">
                <span style="
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #00d4ff;
                    border-radius: 50%;
                    margin: 0 5px;
                    animation: pulse 1.5s ease-in-out infinite;
                "></span>
                <span style="
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #7b2cbf;
                    border-radius: 50%;
                    margin: 0 5px;
                    animation: pulse 1.5s ease-in-out infinite 0.5s;
                "></span>
                <span style="
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #00d4ff;
                    border-radius: 50%;
                    margin: 0 5px;
                    animation: pulse 1.5s ease-in-out infinite 1s;
                "></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
