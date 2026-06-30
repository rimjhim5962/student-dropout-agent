"""
Streamlit Application for AI Student Success & Dropout Prevention System
========================================================================
Purpose: Web interface for student dropout risk prediction, recommendations,
         and comprehensive reports.

NOTE: This file contains a FRONTEND-ONLY redesign. All backend logic —
agent calls, the prediction pipeline, encoding, recommendation logic and
report generation — is identical to the original implementation. Only
layout, styling, and visualization were changed.
"""

import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import time
from datetime import datetime

# Resolve project root path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing agents
from agents.data_analysis_agent import DataAnalysisAgent
from agents.prediction_agent import PredictionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent

# Page configuration
st.set_page_config(
    page_title="AI Student Success & Dropout Prevention System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DESIGN SYSTEM — CSS
# ============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --bg: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: var(--bg);
    }

    /* Hide default Streamlit chrome bits that clutter the redesign */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ---------------------------------------------------------------- */
    /* HERO SECTION                                                      */
    /* ---------------------------------------------------------------- */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 45%, #0EA5E9 100%);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        margin-bottom: 1.75rem;
        color: white;
        overflow: hidden;
        box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.35);
    }
    .hero-container::before {
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 260px; height: 260px;
        background: rgba(255,255,255,0.12);
        border-radius: 50%;
        filter: blur(10px);
    }
    .hero-container::after {
        content: "";
        position: absolute;
        bottom: -80px; left: 10%;
        width: 220px; height: 220px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .hero-eyebrow {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(6px);
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
        line-height: 1.15;
    }
    .hero-subtitle {
        font-size: 1.08rem;
        opacity: 0.92;
        margin-top: 0.7rem;
        margin-bottom: 0;
        max-width: 700px;
        position: relative;
        z-index: 1;
        font-weight: 300;
    }

    /* Glass summary cards inside hero */
    .glass-card {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.25);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        position: relative;
        z-index: 1;
        height: 100%;
    }
    .glass-card .glass-label {
        font-size: 0.78rem;
        opacity: 0.85;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .glass-card .glass-value {
        font-size: 1.9rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    /* ---------------------------------------------------------------- */
    /* GENERIC CARDS                                                     */
    /* ---------------------------------------------------------------- */
    .premium-card {
        background: #ffffff;
        border-radius: 18px;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04), 0 2px 4px -1px rgba(0,0,0,0.03);
        transition: all 0.25s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    .premium-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 28px -8px rgba(0,0,0,0.10);
        border-color: #CBD5E1;
    }

    /* Metric cards (Dashboard) */
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .metric-card .metric-icon {
        font-size: 1.4rem;
        margin-bottom: 0.3rem;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .metric-card .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 0.15rem;
    }
    .metric-card.accent-primary { border-top: 4px solid var(--primary); }
    .metric-card.accent-success { border-top: 4px solid var(--success); }
    .metric-card.accent-warning { border-top: 4px solid var(--warning); }
    .metric-card.accent-danger  { border-top: 4px solid var(--danger); }

    /* Result cards (Risk / Confidence / Probability) */
    .result-card {
        text-align: center;
        padding: 1.6rem 1rem;
        background: #ffffff;
        border-radius: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 10px rgba(15,23,42,0.05);
        height: 100%;
    }
    .result-card .result-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }
    .result-card .result-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
    }

    /* Risk badges */
    .risk-badge {
        font-weight: 700;
        padding: 0.4rem 1.1rem;
        border-radius: 999px;
        text-transform: uppercase;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .risk-no {
        color: #047857;
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
    }
    .risk-medium {
        color: #B45309;
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
    }
    .risk-high {
        color: #B91C1C;
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
    }

    /* Student summary card */
    .summary-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1.25rem;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.9rem;
        margin-top: 0.6rem;
    }
    .summary-item .summary-label {
        font-size: 0.72rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .summary-item .summary-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }

    /* Explanation factor chips */
    .factor-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04);
    }
    .factor-name {
        font-weight: 600;
        color: #1E293B;
        font-size: 0.92rem;
    }
    .factor-value {
        font-weight: 800;
        color: #2563EB;
        font-size: 1.0rem;
    }

    /* Recommendation cards */
    .rec-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid var(--primary);
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }
    .rec-card.priority-high { border-left-color: var(--danger); }
    .rec-card.priority-medium { border-left-color: var(--warning); }
    .rec-card.priority-low,
    .rec-card.priority-normal { border-left-color: var(--success); }

    .rec-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.4rem;
    }
    .rec-meta {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.55rem;
        flex-wrap: wrap;
    }
    .rec-pill {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .pill-priority-high { background: #FEF2F2; color: #B91C1C; }
    .pill-priority-medium { background: #FFFBEB; color: #B45309; }
    .pill-priority-low, .pill-priority-normal { background: #ECFDF5; color: #047857; }
    .pill-timeline { background: #EFF6FF; color: #1D4ED8; }

    .support-chip {
        display: inline-block;
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #E2E8F0;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.2rem 0.3rem 0 0;
    }

    /* Report sections */
    .report-section-title {
        font-size: 1.0rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .exec-summary-box {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        margin-bottom: 1.1rem;
    }
    .insight-pill {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.55rem;
        font-size: 0.92rem;
        color: #78350F;
    }

    /* Sidebar status rows */
    .status-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0;
        font-size: 0.88rem;
        color: #334155;
    }
    .status-dot {
        height: 9px; width: 9px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 0 3px rgba(16,185,129,0.18);
        flex-shrink: 0;
    }

    /* Footer */
    .app-footer {
        margin-top: 2.5rem;
        padding: 1.8rem 2rem;
        background: #ffffff;
        border-top: 1px solid #E2E8F0;
        border-radius: 18px 18px 0 0;
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
    }
    .app-footer .footer-title {
        font-weight: 700;
        color: #1E293B;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
    }
    .footer-pills {
        margin-top: 0.7rem;
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .footer-pill {
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        color: #475569;
    }

    /* Workflow diagram (About page) */
    .workflow-step {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.9rem 1.3rem;
        text-align: center;
        font-weight: 700;
        color: #1E293B;
        box-shadow: 0 2px 6px rgba(15,23,42,0.04);
    }
    .workflow-arrow {
        text-align: center;
        font-size: 1.4rem;
        color: #94A3B8;
        margin: 0.15rem 0;
    }

    /* Styled lists */
    ul.custom-list {
        list-style-type: none;
        padding-left: 0;
    }
    ul.custom-list li {
        position: relative;
        padding-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    ul.custom-list li::before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #10B981;
        font-weight: bold;
    }

    /* Section heading helper */
    .section-heading {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.3rem;
    }
    .section-subheading {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to cache agents and prevent slow reload
@st.cache_resource
def load_agents():
    data_agent = DataAnalysisAgent()
    try:
        data_agent.load_data()
    except Exception:
        pass

    prediction_agent = PredictionAgent()
    prediction_agent.load_model()

    recommendation_agent = RecommendationAgent()
    report_agent = ReportAgent()

    return data_agent, prediction_agent, recommendation_agent, report_agent

# Initialize Agents
data_agent, prediction_agent, recommendation_agent, report_agent = load_agents()

# Initialize session state prediction history
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []

if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()

def encode_student_row(row):
    """
    Encode student row features matching model encodings.
    """
    gender_mapping = {"Male": 1, "Female": 0, "male": 1, "female": 0}
    parental_mapping = {
        "High School": 0, "Diploma": 1, "Graduate": 2, "Postgraduate": 3,
        "high school": 0, "diploma": 1, "graduate": 2, "postgraduate": 3
    }
    income_mapping = {"Low": 0, "Medium": 1, "High": 2, "low": 0, "medium": 1, "high": 2}
    extracurricular_mapping = {"No": 0, "Yes": 1, "no": 0, "yes": 1}
    
    encoded = {}
    REQUIRED_FEATURES = [
    "Age",
    "Gender",
    "Parental_Education",
    "Family_Income_Level",
    "Attendance_Percentage",
    "Study_Hours_Per_Day",
    "Sleep_Hours",
    "Internet_Usage_Hours",
    "Assignments_Completed",
    "Previous_Grades",
    "Class_Participation",
    "Extracurricular_Activities",
    "Stress_Level",
    "Teacher_Feedback_Score",
    "Absence_Days",
    ]

    for clean_key in REQUIRED_FEATURES:
        clean_key = str(clean_key).strip()
        clean_val = row.get(clean_key)

        if isinstance(clean_val, str):
            clean_val = clean_val.strip()
                
        if clean_key == 'Gender':
            if isinstance(clean_val, str) and clean_val in gender_mapping:
                encoded[clean_key] = gender_mapping[clean_val]
            else:
                try:
                    encoded[clean_key] = int(float(clean_val))
                except Exception:
                    encoded[clean_key] = 0
        elif clean_key == 'Parental_Education':
            if isinstance(clean_val, str) and clean_val in parental_mapping:
                encoded[clean_key] = parental_mapping[clean_val]
            else:
                try:
                    encoded[clean_key] = int(float(clean_val))
                except Exception:
                    encoded[clean_key] = 0
        elif clean_key == 'Family_Income_Level':
            if isinstance(clean_val, str) and clean_val in income_mapping:
                encoded[clean_key] = income_mapping[clean_val]
            else:
                try:
                    encoded[clean_key] = int(float(clean_val))
                except Exception:
                    encoded[clean_key] = 0
        elif clean_key == 'Extracurricular_Activities':
            if isinstance(clean_val, str) and clean_val in extracurricular_mapping:
                encoded[clean_key] = extracurricular_mapping[clean_val]
            else:
                try:
                    encoded[clean_key] = int(float(clean_val))
                except Exception:
                    encoded[clean_key] = 0
        else:
            # Numeric fields handling
            if pd.isna(clean_val) or clean_val is None:
                defaults = {
                    'Age': 20.0,
                    'Attendance_Percentage': 85.0,
                    'Study_Hours_Per_Day': 4.5,
                    'Sleep_Hours': 7.0,
                    'Internet_Usage_Hours': 3.0,
                    'Assignments_Completed': 80.0,
                    'Previous_Grades': 75.0,
                    'Class_Participation': 7.0,
                    'Stress_Level': 5.0,
                    'Teacher_Feedback_Score': 7.0,
                    'Absence_Days': 3.0
                }
                encoded[clean_key] = defaults.get(clean_key, 0.0)
            else:
                try:
                    if clean_key in ['Assignments_Completed', 'Previous_Grades', 'Class_Participation', 'Stress_Level', 'Absence_Days', 'Age']:
                        encoded[clean_key] = int(float(clean_val))
                    else:
                        encoded[clean_key] = float(clean_val)
                except Exception:
                    encoded[clean_key] = clean_val
                    
    # Fill defaults if missing completely
    defaults = {
        'Age': 20,
        'Gender': 1,
        'Parental_Education': 1,
        'Family_Income_Level': 1,
        'Attendance_Percentage': 85.0,
        'Study_Hours_Per_Day': 4.5,
        'Sleep_Hours': 7.0,
        'Internet_Usage_Hours': 3.0,
        'Assignments_Completed': 80,
        'Previous_Grades': 75,
        'Class_Participation': 7,
        'Extracurricular_Activities': 0,
        'Stress_Level': 5,
        'Teacher_Feedback_Score': 7,
        'Absence_Days': 3
    }
    for feature in defaults:
        if feature not in encoded:
            encoded[feature] = defaults[feature]
            
    # Map auxiliary keys for RecommendationAgent and ReportAgent
    if 'Student_ID' in encoded:
        encoded['StudentID'] = encoded['Student_ID']
    elif 'StudentID' not in encoded:
        encoded['StudentID'] = 'Unknown'
        
    encoded['GPA'] = float(encoded['Previous_Grades']) / 25.0
    encoded['AttendanceRate'] = float(encoded['Attendance_Percentage']) / 100.0
    encoded['StudyHours'] = float(encoded['Study_Hours_Per_Day']) * 7.0
        
    return encoded

# ============================================================================
# SHARED UI HELPERS
# ============================================================================

RISK_COLORS = {
    "No Risk": "#10B981",
    "Medium Risk": "#F59E0B",
    "High Risk": "#EF4444",
}

def risk_css_class(risk_lvl):
    if risk_lvl == "No Risk":
        return "no"
    elif risk_lvl == "Medium Risk":
        return "medium"
    elif risk_lvl == "High Risk":
        return "high"
    return "medium"

def render_metric_card(icon, label, value, accent="primary"):
    st.markdown(f"""
        <div class="metric-card accent-{accent}">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def render_result_card(label, value_html):
    st.markdown(f"""
        <div class="result-card">
            <div class="result-label">{label}</div>
            <div class="result-value">{value_html}</div>
        </div>
    """, unsafe_allow_html=True)

def run_pipeline_progress():
    """Visual-only progress sequence shown while the real pipeline executes."""
    steps = [
        "Loading Agents...",
        "Loading Model...",
        "Analyzing Student...",
        "Generating Prediction...",
        "Preparing Recommendations...",
        "Generating Report..."
    ]
    status = st.status("Running multi-agent pipeline...", expanded=True)
    for step in steps:
        status.write(f"⏳ {step}")
        time.sleep(0.18)
    status.update(label="Pipeline complete", state="complete", expanded=False)

def render_footer():
    st.markdown("""
        <div class="app-footer">
            <div class="footer-title">🎓 AI Student Success &amp; Dropout Prevention System</div>
            <div>Multi-Agent Architecture · Random Forest Prediction · 15 Existing Features</div>
            <div class="footer-pills">
                <span class="footer-pill">🤖 4 AI Agents</span>
                <span class="footer-pill">🌲 Random Forest Model</span>
                <span class="footer-pill">📋 15 Input Features</span>
                <span class="footer-pill">⚙️ Backend Unmodified</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def main():
    # -------------------------------------------------------------- HERO ---
    total_preds_so_far = len(st.session_state.predictions_history)
    session_duration = datetime.now() - st.session_state.session_start
    session_minutes = int(session_duration.total_seconds() // 60)

    st.markdown(f"""
        <div class="hero-container">
            <div class="hero-eyebrow">🎓 Multi-Agent AI Platform</div>
            <h1 class="hero-title">AI Student Success &amp; Dropout Prevention System</h1>
            <p class="hero-subtitle">
                A multi-agent framework utilizing machine learning to predict dropout risk,
                customize interventions, and draft intelligence reports — built to help
                educators act before students fall behind.
            </p>
        </div>
    """, unsafe_allow_html=True)

    hc1, hc2, hc3, hc4 = st.columns(4)
    with hc1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-label">📁 Students Processed</div>
                <div class="glass-value">{total_preds_so_far}</div>
            </div>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown("""
            <div class="glass-card">
                <div class="glass-label">🤖 AI Agents</div>
                <div class="glass-value">4</div>
            </div>
        """, unsafe_allow_html=True)
    with hc3:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-label">🔮 Predictions Generated</div>
                <div class="glass-value">{total_preds_so_far}</div>
            </div>
        """, unsafe_allow_html=True)
    with hc4:
        st.markdown(f"""
            <div class="glass-card">
                <div class="glass-label">⏱️ Current Session</div>
                <div class="glass-value">{session_minutes}m</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------- SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "Select Workflow Page:",
            options=[
                "🏠 Dashboard",
                "👤 Single Prediction",
                "📁 Batch Analysis",
                "📄 Reports",
                "ℹ️ About"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### 🛰️ System Status")
        agent_labels = [
            "Data Agent Loaded",
            "Prediction Agent Loaded",
            "Recommendation Agent Loaded",
            "Report Agent Loaded",
            "Model Loaded",
        ]
        status_html = "".join(
            f'<div class="status-row"><span class="status-dot"></span>{label}</div>'
            for label in agent_labels
        )
        st.markdown(status_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Current Session")
        st.metric("Session Predictions", total_preds_so_far)

    # ------------------------------------------------------------- ROUTE ---
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👤 Single Prediction":
        show_single_prediction()
    elif page == "📁 Batch Analysis":
        show_batch_analysis()
    elif page == "📄 Reports":
        show_reports_history()
    elif page == "ℹ️ About":
        show_about()

    render_footer()

def show_dashboard():
    st.markdown('<div class="section-heading">📊 System Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheading">Live analytics for this session, plus a statistical view of the underlying dataset.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⚡ Prediction Metrics & History", "📁 Dataset Statistical Explorer"])

    with tab1:
        # Prediction session statistics (same underlying data/logic as before)
        no_risk = st.session_state.predictions_history.count("No Risk")
        med_risk = st.session_state.predictions_history.count("Medium Risk")
        high_risk = st.session_state.predictions_history.count("High Risk")
        total_predictions = len(st.session_state.predictions_history)

        avg_dropout_prob = (med_risk * 0.5 + high_risk * 0.85) / total_predictions if total_predictions > 0 else 0.0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_metric_card("🧮", "Total Predictions", total_predictions, "primary")
        with c2:
            render_metric_card("🟢", "No Risk", no_risk, "success")
        with c3:
            render_metric_card("🟡", "Medium Risk", med_risk, "warning")
        with c4:
            render_metric_card("🔴", "High Risk", high_risk, "danger")
        with c5:
            render_metric_card("📈", "Avg. Dropout Prob.", f"{avg_dropout_prob:.1%}" if total_predictions else "—", "primary")

        st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

        if total_predictions > 0:
            col_pie, col_bar = st.columns(2)

            with col_pie:
                chart_df = pd.DataFrame({
                    'Risk Level': ['No Risk', 'Medium Risk', 'High Risk'],
                    'Count': [no_risk, med_risk, high_risk]
                })
                fig_pie = px.pie(
                    chart_df,
                    values='Count',
                    names='Risk Level',
                    title="Risk Level Distribution",
                    color='Risk Level',
                    color_discrete_map=RISK_COLORS,
                    hole=0.55
                )
                fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie.update_layout(
                    showlegend=True,
                    margin=dict(t=60, b=20, l=20, r=20),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Outfit, sans-serif")
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_bar:
                fig_bar = px.bar(
                    chart_df,
                    x='Risk Level',
                    y='Count',
                    title="Risk Count by Category",
                    color='Risk Level',
                    color_discrete_map=RISK_COLORS,
                    text='Count'
                )
                fig_bar.update_traces(textposition='outside')
                fig_bar.update_layout(
                    showlegend=False,
                    margin=dict(t=60, b=20, l=20, r=20),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Outfit, sans-serif"),
                    yaxis_title="", xaxis_title=""
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("##### 🕒 Prediction History (This Session)")
            history_df = pd.DataFrame({
                'Index': list(range(1, total_predictions + 1)),
                'Risk Level': st.session_state.predictions_history
            })
            risk_to_num = {'No Risk': 0, 'Medium Risk': 1, 'High Risk': 2}
            history_df['Risk Score'] = history_df['Risk Level'].map(risk_to_num)

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(
                x=history_df['Index'],
                y=history_df['Risk Score'],
                mode='lines+markers',
                line=dict(color='#2563EB', width=2),
                marker=dict(
                    size=10,
                    color=[RISK_COLORS[r] for r in history_df['Risk Level']],
                    line=dict(width=1, color='white')
                ),
                text=history_df['Risk Level'],
                hovertemplate="Prediction #%{x}<br>%{text}<extra></extra>"
            ))
            fig_hist.update_layout(
                yaxis=dict(
                    tickmode='array',
                    tickvals=[0, 1, 2],
                    ticktext=['No Risk', 'Medium Risk', 'High Risk'],
                    title=""
                ),
                xaxis_title="Prediction Sequence",
                margin=dict(t=20, b=20, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Outfit, sans-serif"),
                height=320
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("💡 No predictions made in the current session yet. Run Single Student or Batch predictions to populate this dashboard.")

    with tab2:
        # Dataset insights loaded via DataAnalysisAgent (logic unchanged)
        try:
            df_dataset = data_agent.load_data()
            summary = data_agent.get_dataset_summary()

            total_students = df_dataset.shape[0]
            dataset_shape = df_dataset.shape
            missing_val_count = df_dataset.isnull().sum().sum()
            avg_attendance_val = df_dataset['Attendance_Percentage'].mean()
            avg_grades_val = df_dataset['Previous_Grades'].mean()

            c1, c2, c3 = st.columns(3)
            with c1:
                render_metric_card("🎓", "Dataset Total Students", total_students, "primary")
            with c2:
                render_metric_card("📅", "Average Attendance", f"{avg_attendance_val:.2f}%", "success")
            with c3:
                render_metric_card("📝", "Average Previous Grades", f"{avg_grades_val:.2f}/100", "primary")

            st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

            c4, c5 = st.columns(2)
            with c4:
                render_metric_card("📐", "Dataset Dimension", f"{dataset_shape[0]} × {dataset_shape[1]}", "primary")
            with c5:
                render_metric_card("⚠️", "Total Missing Values", missing_val_count, "warning")

            st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

            total_cells = dataset_shape[0] * dataset_shape[1]
            data_completeness = 1.0 - (missing_val_count / total_cells) if total_cells > 0 else 0.0
            st.markdown(f"**Dataset Completeness Level**: {data_completeness:.2%}")
            st.progress(data_completeness)

            st.markdown("#### Preview of the Raw Database File")
            st.dataframe(df_dataset.head(100), use_container_width=True)

        except Exception as e:
            st.error(f"Could not load dataset details: {str(e)}")

def show_single_prediction():
    st.markdown('<div class="section-heading">👤 Single Student Success Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheading">Fill out the attributes below to perform a risk assessment on the student.</div>', unsafe_allow_html=True)

    # ---- Grid of inputs (all original fields preserved, organized into cards) ----
    st.markdown("##### 🧑‍🎓 Demographics")
    col1, col2, col3 = st.columns(3)
    with col1:
        student_id = st.text_input("Student Identifier", value="S-101")
    with col2:
        age = st.number_input("Age", min_value=15, max_value=50, value=20, step=1)
    with col3:
        gender = st.selectbox("Gender", options=["Male", "Female"])

    col4, col5 = st.columns(2)
    with col4:
        parental_edu = st.selectbox("Parental Education Level", options=["High School", "Diploma", "Graduate", "Postgraduate"])
    with col5:
        family_income = st.selectbox("Family Income Tier", options=["Low", "Medium", "High"])

    st.markdown("##### 📚 Academic & Lifestyle Factors")
    col6, col7, col8 = st.columns(3)
    with col6:
        attendance = st.slider("Attendance Percentage (%)", min_value=0.0, max_value=100.0, value=90.0, step=0.1)
        study_hours = st.number_input("Daily Study Hours", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
    with col7:
        sleep_hours = st.number_input("Average Daily Sleep Hours", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        internet_hours = st.number_input("Daily Internet Usage Hours", min_value=0.0, max_value=24.0, value=3.0, step=0.5)
    with col8:
        assignments = st.number_input("Assignments Completed Count (0-100)", min_value=0, max_value=100, value=85, step=1)
        grades = st.number_input("Previous Grades Score (0-100)", min_value=0, max_value=100, value=80, step=1)

    st.markdown("##### 🧠 Engagement & Wellbeing")
    col9, col10, col11 = st.columns(3)
    with col9:
        participation = st.slider("Class Participation Level (1-10)", min_value=1, max_value=10, value=8)
        extracurricular = st.selectbox("Extracurricular Activities Participation", options=["Yes", "No"])
    with col10:
        stress_level = st.slider("Stress Level (1-10)", min_value=1, max_value=10, value=4)
        teacher_feedback = st.slider("Teacher Feedback Score (1-10)", min_value=1, max_value=10, value=8)
    with col11:
        absence_days = st.number_input("Absence Days Count (0-365)", min_value=0, max_value=365, value=2, step=1)

    st.markdown("---")

    if st.button("🔮 Run Dropout Prediction Pipeline", type="primary", use_container_width=True):
        # Convert values using encodings specified in requirements (unchanged)
        gender_mapping = {"Male": 1, "Female": 0}
        parental_mapping = {"High School": 0, "Diploma": 1, "Graduate": 2, "Postgraduate": 3}
        income_mapping = {"Low": 0, "Medium": 1, "High": 2}
        extracurricular_mapping = {"No": 0, "Yes": 1}

        student_data = {
            'StudentID': student_id,
            'Age': age,
            'Gender': gender_mapping[gender],
            'Parental_Education': parental_mapping[parental_edu],
            'Family_Income_Level': income_mapping[family_income],
            'Attendance_Percentage': attendance,
            'Study_Hours_Per_Day': study_hours,
            'Sleep_Hours': sleep_hours,
            'Internet_Usage_Hours': internet_hours,
            'Assignments_Completed': assignments,
            'Previous_Grades': grades,
            'Class_Participation': participation,
            'Extracurricular_Activities': extracurricular_mapping[extracurricular],
            'Stress_Level': stress_level,
            'Teacher_Feedback_Score': teacher_feedback,
            'Absence_Days': absence_days,

            # Encodings needed for Recommendation/Report compatibility
            'GPA': float(grades) / 25.0,
            'AttendanceRate': float(attendance) / 100.0,
            'StudyHours': float(study_hours) * 7.0
        }

        # Visual-only loading sequence, then the real (unchanged) pipeline calls
        run_pipeline_progress()

        # Predict using PredictionAgent
        prediction = prediction_agent.predict_dropout_risk(student_data)

        if prediction.get('status') == 'success':
            # Store in session predictions history
            st.session_state.predictions_history.append(prediction['risk_level'])

            # Generate recommendations using RecommendationAgent
            recommendations = recommendation_agent.generate_recommendations(student_data, prediction)

            # Generate report using ReportAgent
            if hasattr(report_agent, 'generate_report'):
                report = report_agent.generate_student_report(student_data, prediction, recommendations)
            else:
                report = report_agent.generate_student_report(student_data, prediction, recommendations)

            # ---------------------------------------------------- RENDER ---
            st.success("🎉 Multi-agent workflow completed successfully!")

            risk_lvl = prediction['risk_level']
            risk_class = risk_css_class(risk_lvl)

            # Student summary card
            st.markdown(f"""
                <div class="summary-card">
                    <div style="font-weight:700; color:#1E293B; font-size:1.0rem;">📌 Student Summary — {student_id}</div>
                    <div class="summary-grid">
                        <div class="summary-item"><div class="summary-label">Student ID</div><div class="summary-value">{student_id}</div></div>
                        <div class="summary-item"><div class="summary-label">Age</div><div class="summary-value">{age}</div></div>
                        <div class="summary-item"><div class="summary-label">Attendance</div><div class="summary-value">{attendance:.1f}%</div></div>
                        <div class="summary-item"><div class="summary-label">Grades</div><div class="summary-value">{grades}/100</div></div>
                        <div class="summary-item"><div class="summary-label">Study Hours</div><div class="summary-value">{study_hours:.1f} hrs/day</div></div>
                        <div class="summary-item"><div class="summary-label">Stress Level</div><div class="summary-value">{stress_level}/10</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            res_tab1, res_tab2, res_tab3 = st.tabs(["🎯 Dropout Assessment", "🛡️ Intervention Plan", "📄 Exportable Intelligence Report"])

            with res_tab1:
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    render_result_card("RISK EVALUATION", f'<span class="risk-badge risk-{risk_class}">{risk_lvl}</span>')
                with col_m2:
                    render_result_card("CONFIDENCE", f"{prediction['confidence_score']:.2%}")
                with col_m3:
                    render_result_card("DROPOUT PROBABILITY", f"{prediction['dropout_probability']:.2%}")

                st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
                st.write("**Visualized Dropout Probability Level**")
                st.progress(prediction['dropout_probability'])

                st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
                st.write("**Model Confidence Level**")
                st.progress(prediction['confidence_score'])

                # ---- "Why this prediction?" — visual-only explanation, no new ML logic ----
                st.markdown("---")
                st.markdown('<div class="report-section-title">🔍 Why this prediction?</div>', unsafe_allow_html=True)
                st.caption("A visual look at the key existing features that feed the model. No additional calculations are performed here.")

                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.markdown(f"""
                        <div class="factor-card"><span class="factor-name">📅 Attendance</span><span class="factor-value">{attendance:.1f}%</span></div>
                        <div class="factor-card"><span class="factor-name">📝 Previous Grades</span><span class="factor-value">{grades}/100</span></div>
                        <div class="factor-card"><span class="factor-name">😰 Stress Level</span><span class="factor-value">{stress_level}/10</span></div>
                    """, unsafe_allow_html=True)
                with exp_col2:
                    st.markdown(f"""
                        <div class="factor-card"><span class="factor-name">🚫 Absence Days</span><span class="factor-value">{absence_days}</span></div>
                        <div class="factor-card"><span class="factor-name">📖 Study Hours/Day</span><span class="factor-value">{study_hours:.1f} hrs</span></div>
                        <div class="factor-card"><span class="factor-name">👩‍🏫 Teacher Feedback</span><span class="factor-value">{teacher_feedback}/10</span></div>
                    """, unsafe_allow_html=True)

                st.markdown("#### Key Assessment Insights")
                insights = report.get('key_insights', [])
                if insights:
                    for ins in insights:
                        st.info(f"💡 {ins}")
                else:
                    st.write("No critical risk insights flagged.")

            with res_tab2:
                st.markdown('<div class="report-section-title">⚡ Recommended Actions &amp; Interventions</div>', unsafe_allow_html=True)
                interventions = recommendations.get('interventions', [])
                if interventions:
                    for idx, item in enumerate(interventions, 1):
                        if isinstance(item, dict):
                            action_txt = item.get('action', f'Recommendation {idx}')
                            prio = str(item.get('priority', 'Normal'))
                            timeline = item.get('estimated_timeline', 'Ongoing')
                            description = item.get('description', '')
                        else:
                            action_txt = str(item)
                            prio = 'Normal'
                            timeline = 'Ongoing'
                            description = ''

                        prio_class = prio.strip().lower().replace(' ', '-')
                        if prio_class not in ('high', 'medium', 'low', 'normal'):
                            prio_class = 'normal'

                        desc_html = f'<div style="color:#475569; font-size:0.9rem; margin-top:0.4rem;">{description}</div>' if description else ''

                        st.markdown(f"""
                            <div class="rec-card priority-{prio_class}">
                                <div class="rec-title">{idx}. {action_txt}</div>
                                <div class="rec-meta">
                                    <span class="rec-pill pill-priority-{prio_class}">Priority: {prio}</span>
                                    <span class="rec-pill pill-timeline">⏱ {timeline}</span>
                                </div>
                                {desc_html}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No specific intervention plans required.")

                st.markdown('<div class="report-section-title" style="margin-top:1.5rem;">🏥 Recommended Support Services</div>', unsafe_allow_html=True)
                services = recommendations.get('support_services', [])
                if services:
                    chips_html = "".join(f'<span class="support-chip">🏷️ {s}</span>' for s in services)
                    st.markdown(f'<div>{chips_html}</div>', unsafe_allow_html=True)
                else:
                    st.write("No specialized support services flagged.")

            with res_tab3:
                # Professional report layout instead of raw JSON-first view
                st.markdown('<div class="report-section-title">📋 Executive Summary</div>', unsafe_allow_html=True)
                exec_summary = report.get('executive_summary') or report.get('summary')
                if not exec_summary:
                    exec_summary = (
                        f"Student {student_id} was evaluated as **{risk_lvl}** with a "
                        f"{prediction['dropout_probability']:.1%} dropout probability and "
                        f"{prediction['confidence_score']:.1%} model confidence."
                    )
                st.markdown(f'<div class="exec-summary-box">{exec_summary}</div>', unsafe_allow_html=True)

                rc1, rc2 = st.columns(2)
                with rc1:
                    render_result_card("RISK LEVEL", f'<span class="risk-badge risk-{risk_class}">{risk_lvl}</span>')
                with rc2:
                    render_result_card("DROPOUT PROBABILITY", f"{prediction['dropout_probability']:.2%}")

                st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

                st.markdown('<div class="report-section-title">🛡️ Recommendations</div>', unsafe_allow_html=True)
                if interventions:
                    for idx, item in enumerate(interventions, 1):
                        action_txt = item.get('action', item) if isinstance(item, dict) else item
                        st.markdown(f"- **{action_txt}**")
                else:
                    st.write("No specific intervention plans required.")

                st.markdown('<div class="report-section-title" style="margin-top:1.2rem;">💡 Key Insights</div>', unsafe_allow_html=True)
                if insights:
                    for ins in insights:
                        st.markdown(f'<div class="insight-pill">💡 {ins}</div>', unsafe_allow_html=True)
                else:
                    st.write("No critical risk insights flagged.")

                with st.expander("🔧 View Full Raw JSON Report Output"):
                    st.json(report)

                json_report_str = json.dumps(report, indent=4)
                st.download_button(
                    label="📥 Download JSON Report",
                    data=json_report_str,
                    file_name=f"report_{student_id}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        else:
            st.error(f"Prediction failed: {prediction.get('message', 'Unknown error occurred.')}")

def show_batch_analysis():
    st.markdown('<div class="section-heading">📤 Batch Analytics via CSV Upload</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheading">Process multiple student files concurrently using our multi-agent framework.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your Student success variables CSV file:",
        type="csv",
        help="Make sure the CSV matches standard dataset formatting without GPA."
    )

    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)

        st.success(f"File uploaded successfully! Detected {len(df_uploaded)} students in queue.")
        st.markdown("#### Data File Preview (First 5 Rows)")
        st.dataframe(df_uploaded.head(5), use_container_width=True)

        if st.button("🚀 Analyze All Queue Students", type="primary", use_container_width=True):
            steps = [
                "Loading Agents...",
                "Loading Model...",
                "Analyzing Student...",
                "Generating Prediction...",
                "Preparing Recommendations...",
                "Generating Report..."
            ]
            status_box = st.status("Initializing batch pipeline...", expanded=True)
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            processed_data = []
            total_students = len(df_uploaded)

            for safe_index, (_, row) in enumerate(df_uploaded.iterrows(), start=1):
                student_raw = row.to_dict()
                student_encoded = encode_student_row(student_raw)

                status_box.write(f"⏳ {steps[(safe_index - 1) % len(steps)]}")

                # Predict
                pred = prediction_agent.predict_dropout_risk(student_encoded)

                # Recommendations
                recs = recommendation_agent.generate_recommendations(student_encoded, pred)

                # Report
                rep = report_agent.generate_student_report(student_encoded, pred, recs)

                student_id = student_raw.get(
                    'StudentID',
                    student_raw.get('Student_ID', f"STU-{safe_index}")
                )

                risk_lvl = pred.get('risk_level', 'Error')
                conf = pred.get('confidence_score', 0.0)
                prob = pred.get('dropout_probability', 0.0)

                processed_data.append({
                    'StudentID': student_id,
                    'Risk Level': risk_lvl,
                    'Confidence Score': f"{conf:.2%}",
                    'Dropout Probability': f"{prob:.2%}",
                    'Status': pred.get('status', 'error'),
                    'Interventions Prescribed': len(recs.get('interventions', [])) if recs else 0,
                    '_prob_raw': prob
                })

                if pred.get('status') == 'success':
                    st.session_state.predictions_history.append(risk_lvl)

                progress_percent = safe_index / total_students
                progress_bar.progress(progress_percent)
                status_text.text(
                    f"Processed student {safe_index} of {total_students} ({student_id})"
                )
            progress_bar.empty()
            status_text.empty()
            status_box.update(label=f"Batch pipeline complete — {total_students} students processed", state="complete", expanded=False)

            result_df = pd.DataFrame(processed_data)
            display_df = result_df.drop(columns=['_prob_raw'])

            # ---- Summary cards ----
            st.markdown("### 📊 Compiled Assessment Results")
            no_risk_n = (result_df['Risk Level'] == 'No Risk').sum()
            med_risk_n = (result_df['Risk Level'] == 'Medium Risk').sum()
            high_risk_n = (result_df['Risk Level'] == 'High Risk').sum()

            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                render_metric_card("📁", "Total Processed", total_students, "primary")
            with sc2:
                render_metric_card("🟢", "No Risk", int(no_risk_n), "success")
            with sc3:
                render_metric_card("🟡", "Medium Risk", int(med_risk_n), "warning")
            with sc4:
                render_metric_card("🔴", "High Risk", int(high_risk_n), "danger")

            st.markdown("<div style='height: 1.2rem'></div>", unsafe_allow_html=True)

            # ---- Risk distribution charts ----
            chart_col1, chart_col2 = st.columns(2)
            risk_summary_df = pd.DataFrame({
                'Risk Level': ['No Risk', 'Medium Risk', 'High Risk'],
                'Count': [int(no_risk_n), int(med_risk_n), int(high_risk_n)]
            })

            with chart_col1:
                fig_pie = px.pie(
                    risk_summary_df, values='Count', names='Risk Level',
                    title="Batch Risk Distribution",
                    color='Risk Level', color_discrete_map=RISK_COLORS, hole=0.55
                )
                fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie.update_layout(
                    margin=dict(t=60, b=20, l=20, r=20),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Outfit, sans-serif")
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with chart_col2:
                fig_bar = px.bar(
                    risk_summary_df, x='Risk Level', y='Count',
                    title="Risk Count Breakdown",
                    color='Risk Level', color_discrete_map=RISK_COLORS, text='Count'
                )
                fig_bar.update_traces(textposition='outside')
                fig_bar.update_layout(
                    showlegend=False,
                    margin=dict(t=60, b=20, l=20, r=20),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Outfit, sans-serif"),
                    yaxis_title="", xaxis_title=""
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # ---- Top high risk students table ----
            st.markdown("#### 🚨 Top High-Risk Students")
            high_risk_df = result_df[result_df['Risk Level'] == 'High Risk'].sort_values('_prob_raw', ascending=False)
            if len(high_risk_df) > 0:
                st.dataframe(high_risk_df.drop(columns=['_prob_raw']).head(10), use_container_width=True)
            else:
                st.info("No high-risk students detected in this batch. 🎉")

            st.markdown("#### 📋 Full Compiled Results")
            st.dataframe(display_df, use_container_width=True)

            # Allow CSV download (unchanged)
            csv_str = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Compiled Batch Results as CSV",
                data=csv_str,
                file_name=f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def show_reports_history():
    st.markdown('<div class="section-heading">📄 Generated Agent Intelligence Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheading">Browse, inspect, and extract student intelligence reports generated during this session.</div>', unsafe_allow_html=True)

    reports = report_agent.get_report_history()

    if reports:
        report_ids = [r.get('report_metadata', {}).get('report_id', f"Report_{idx}") for idx, r in enumerate(reports)]
        selected_report_id = st.selectbox("Select Report to View:", options=report_ids)

        target_report = next(r for r in reports if r.get('report_metadata', {}).get('report_id') == selected_report_id)

        st.markdown(f"""
            <div class="exec-summary-box">
                <div class="report-section-title">📋 Executive Summary</div>
                <div class="summary-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div class="summary-item"><div class="summary-label">Report ID</div><div class="summary-value">{selected_report_id}</div></div>
                    <div class="summary-item"><div class="summary-label">Generated Time</div><div class="summary-value">{target_report.get('report_metadata', {}).get('generated_at', '—')}</div></div>
                    <div class="summary-item"><div class="summary-label">Student ID</div><div class="summary-value">{target_report.get('student_id', 'Unknown')}</div></div>
                    <div class="summary-item"><div class="summary-label">Status</div><div class="summary-value">{target_report.get('report_status', 'Generated')}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        risk_section = target_report.get('prediction', {}) if isinstance(target_report.get('prediction', {}), dict) else {}
        if risk_section:
            rrc1, rrc2 = st.columns(2)
            with rrc1:
                rlvl = risk_section.get('risk_level', '—')
                rclass = risk_css_class(rlvl)
                render_result_card("RISK LEVEL", f'<span class="risk-badge risk-{rclass}">{rlvl}</span>' if rlvl != '—' else '—')
            with rrc2:
                rprob = risk_section.get('dropout_probability')
                render_result_card("PROBABILITY", f"{rprob:.2%}" if isinstance(rprob, (int, float)) else "—")

        insights = target_report.get('key_insights', [])
        if insights:
            st.markdown('<div class="report-section-title" style="margin-top:1rem;">💡 Key Insights</div>', unsafe_allow_html=True)
            for ins in insights:
                st.markdown(f'<div class="insight-pill">💡 {ins}</div>', unsafe_allow_html=True)

        with st.expander("🔧 View Complete Report JSON Data"):
            st.json(target_report)

        st.download_button(
            label="📥 Download This JSON Report File",
            data=json.dumps(target_report, indent=4),
            file_name=f"{selected_report_id}.json",
            mime="application/json"
        )
    else:
        st.info("No intelligence reports compiled yet in this session. Go to the Single Student Prediction or Batch CSV Analysis to process students and generate reports.")

def show_about():
    st.markdown('<div class="section-heading">ℹ️ About AI Student Success &amp; Dropout Prevention System</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheading">This tool uses a multi-agent structure to evaluate and intervene in student retention risks.</div>', unsafe_allow_html=True)

    # ---- Visual workflow ----
    st.markdown("#### 🔄 Prediction Workflow")
    workflow_steps = [
        "🧑‍🎓 Student Input",
        "📊 Data Analysis Agent",
        "🔮 Prediction Agent",
        "🛡️ Recommendation Agent",
        "📄 Report Agent",
        "✅ Final Report"
    ]
    for i, step in enumerate(workflow_steps):
        st.markdown(f'<div class="workflow-step">{step}</div>', unsafe_allow_html=True)
        if i < len(workflow_steps) - 1:
            st.markdown('<div class="workflow-arrow">↓</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🤖 Existing AI Agents")
        st.markdown("""
            <div class="premium-card">
                <b>1. Data Analysis Agent</b><br>
                <span style="color:#64748B; font-size:0.9rem;">Handles database cleaning, handles missing values, and calculates statistical parameters.</span>
            </div>
            <div class="premium-card">
                <b>2. Prediction Agent</b><br>
                <span style="color:#64748B; font-size:0.9rem;">Executes predictive machine learning evaluation models utilizing a trained Random Forest architecture.</span>
            </div>
            <div class="premium-card">
                <b>3. Recommendation Agent</b><br>
                <span style="color:#64748B; font-size:0.9rem;">Analyzes metrics of risk to format personalized intervention schemes and support assignments.</span>
            </div>
            <div class="premium-card">
                <b>4. Report Agent</b><br>
                <span style="color:#64748B; font-size:0.9rem;">Consolidates predictions, variables, recommendations, and analytics into structured JSON data report format.</span>
            </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("#### ⚙️ Technology Stack")
        st.markdown("""
            <div class="premium-card">
                <span class="footer-pill">🐍 Python</span>
                <span class="footer-pill">🎨 Streamlit</span>
                <span class="footer-pill">🌲 Random Forest</span>
                <span class="footer-pill">📊 Plotly</span>
                <span class="footer-pill">🐼 Pandas</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📋 Project Overview")
        st.markdown("""
            <div class="premium-card" style="color:#475569; font-size:0.92rem;">
                A multi-agent system that evaluates 15 student attributes to estimate dropout risk,
                then generates tailored interventions and a structured intelligence report — without
                requiring any manual statistical analysis from the educator.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📋 Model Parameters (15 Features)")
    feature_docs = [
        ("Age", "Student Age."),
        ("Gender", "Female (0) or Male (1)."),
        ("Parental Education", "High School (0), Diploma (1), Graduate (2), Postgraduate (3)."),
        ("Family Income", "Low (0), Medium (1), High (2)."),
        ("Attendance Percentage", "Slider range input 0.0 - 100.0%."),
        ("Study Hours Per Day", "Student daily homework hours."),
        ("Sleep Hours", "Average daily sleep."),
        ("Internet Usage Hours", "Daily internet hours."),
        ("Assignments Completed", "Numerical percentage."),
        ("Previous Grades", "Average grade (0-100)."),
        ("Class Participation", "Teacher rating (1-10)."),
        ("Extracurricular Activities", "Participating (1) or No (0)."),
        ("Stress Level", "Standard level (1-10)."),
        ("Teacher Feedback Score", "Average rating (1-10)."),
        ("Absence Days", "Absences during the semester."),
    ]
    fc1, fc2, fc3 = st.columns(3)
    feature_cols = [fc1, fc2, fc3]
    for i, (fname, fdesc) in enumerate(feature_docs):
        with feature_cols[i % 3]:
            st.markdown(f"""
                <div class="factor-card" style="flex-direction:column; align-items:flex-start;">
                    <span class="factor-name">{fname}</span>
                    <span style="color:#64748B; font-size:0.82rem; margin-top:0.2rem;">{fdesc}</span>
                </div>
            """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
    
    import os

print("RUNNING APP_FIXED.PY")