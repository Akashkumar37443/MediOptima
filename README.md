# 🏥 MediOptima

**AI-Powered Hospital Resource Optimization System**

MediOptima is an intelligent healthcare management platform that uses AI-driven forecasting and optimization to predict hospital demand and optimize resources including beds, staff, and ICU capacity.

## ✨ Features

### 1. 📈 Patient Inflow Prediction
- **Time-series forecasting** using Facebook Prophet
- Predicts patient volume for next 7/30 days
- Seasonality detection (weekly, yearly patterns)
- Confidence intervals for uncertainty quantification

### 2. 🛏️ Bed Requirement Estimation
- Real-time bed utilization tracking
- 7-day bed demand forecasting with 15% emergency buffer
- Shortage risk assessment (Critical/High/Medium/Low)
- General ward and ICU separate tracking

### 3. 👨‍⚕️ Staff Scheduling Optimization
- **Linear Programming** optimization using PuLP
- Optimizes doctor, nurse, and ICU nurse allocation
- Constraint-based optimization:
  - 1 Doctor per 20 patients
  - 1 Nurse per 8 patients  
  - 1 ICU Nurse per 2 ICU patients
- Cost minimization while meeting all requirements

### 4. 🚨 Surge & Anomaly Detection
- **Z-score** statistical anomaly detection
- **Isolation Forest** machine learning anomalies
- Surge pattern detection (sustained high demand)
- Real-time system status monitoring
- Critical/High/Elevated/Normal alert levels

### 5. 🤖 AI Insight Generator
- Automated executive summaries
- Resource shortage alerts
- Prioritized action items
- Trend analysis and recommendations

### 6. 📊 Interactive Dashboard (Streamlit)
- KPI cards with real-time metrics
- Historical vs forecast visualizations
- Bed utilization gauges
- Staff schedule tables
- Anomaly detection charts
- Downloadable insights

## 🚀 Quick Start

### Installation

```bash
cd MediOptima
pip install -r requirements.txt
```

### Generate Synthetic Data

```bash
python data_generator.py
```

### Run Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
MediOptima/
├── app.py                    # Main Streamlit dashboard
├── data_generator.py         # Synthetic hospital data generator
├── requirements.txt          # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── forecasting.py        # Prophet-based forecasting
│   ├── bed_optimizer.py      # Bed requirement calculations
│   ├── staff_optimizer.py    # Linear programming staff optimization
│   ├── anomaly_detector.py   # Z-score & Isolation Forest anomalies
│   └── insight_generator.py  # AI insight generation
├── hospital_data.csv         # Generated dataset
└── README.md
```

## 🛠️ Technologies Used

| Component | Technology |
|-----------|------------|
| Programming | Python 3.8+ |
| Forecasting | Prophet, Scikit-learn |
| Optimization | PuLP (Linear Programming) |
| ML/Anomaly Detection | Isolation Forest, Z-score |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data | Pandas, NumPy |

## 📊 Data Fields

- **Date** - Daily timestamp
- **Daily_Patients** - Total patient admissions
- **Emergency_Cases** - Emergency department visits
- **ICU_Admissions** - ICU bed admissions
- **Discharge_Count** - Daily discharges
- **Available_Beds** - General ward available beds
- **Available_ICU_Beds** - ICU available beds
- **Doctors_On_Duty** - Number of doctors
- **Nurses_On_Duty** - Number of nurses
- **ICU_Nurses** - Number of ICU nurses
- **Is_Holiday** - Binary holiday indicator
- **Temperature** - Weather data (affects respiratory cases)

## 🎯 Use Cases

1. **Daily Planning** - Morning briefing with 7-day forecast
2. **Capacity Management** - Bed allocation and shortage prevention
3. **Staffing Decisions** - Optimize nurse/doctor schedules
4. **Emergency Preparedness** - Detect and respond to surges
5. **Executive Reporting** - Automated insight generation

## 📈 Model Performance

The forecasting models are evaluated using:
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)

## 🔮 Future Enhancements

- Real-time data integration (HL7 FHIR)
- Multi-hospital network optimization
- Pandemic outbreak detection models
- Ambulance routing integration
- AI chatbot for hospital admin

## 📄 License

MIT License - Built for healthcare optimization

---

**Built with ❤️ for better healthcare resource management**
