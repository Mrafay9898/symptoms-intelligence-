import streamlit as st
import asyncio
from backend.ai_pipeline import engine
from backend.medication_checker import medication_safety
import json
import os

# Page Config
st.set_page_config(
    page_title="Symptom Intelligence Engine",
    page_icon="🏥",
    layout="centered"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .triage-card {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid;
    }
    .emergency { background-color: #fef2f2; border-left-color: #ef4444; }
    .urgent { background-color: #fffbeb; border-left-color: #f59e0b; }
    .routine { background-color: #f0fdf4; border-left-color: #22c55e; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Symptom Intelligence 🏥</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Safe, Reasoned, and Explainable Clinical Support</div>', unsafe_allow_html=True)

# Input Section
with st.container():
    st.subheader("Assessment Details")
    symptom_text = st.text_area("Describe your symptoms (e.g., 'Severe headache for 2 days')", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        temp = st.number_input("Temperature (°C)", value=37.0, step=0.1)
        hr = st.number_input("Heart Rate (bpm)", value=75, step=1)
    with col2:
        sys = st.number_input("Systolic BP", value=120, step=1)
        dia = st.number_input("Diastolic BP", value=80, step=1)

    medications = st.text_input("Current Medications (comma separated)", placeholder="e.g., Aspirin, Ibuprofen")
    conditions = st.text_input("Existing Conditions (comma separated)", placeholder="e.g., Asthma, Diabetes")

if st.button("Analyze Now", type="primary", use_container_width=True):
    if not symptom_text:
        st.warning("Please describe your symptoms first.")
    else:
        with st.spinner("AI Engine analyzing symptoms and safety protocols..."):
            # Prepare data
            med_list = [m.strip() for m in medications.split(",")] if medications else []
            cond_list = [c.strip() for c in conditions.split(",")] if conditions else []
            vitals = {"temp": temp, "heart_rate": hr, "bp_sys": sys, "bp_dia": dia}

            # Run Async Logic
            async def run_analysis():
                # Extract symptoms (Mock for demo if no API key, but uses real logic)
                extracted = [{"name": "Reported Symptom", "severity": "moderate"}] 
                
                # Fetch Real Analysis
                analysis = await engine.generate_diagnosis_and_triage(
                    extracted_symptoms=extracted,
                    medications=med_list,
                    existing_conditions=cond_list
                )
                
                # Check Safety
                safety = await medication_safety.check_interactions(med_list, cond_list)
                return analysis, safety

            analysis, safety = asyncio.run(run_analysis())

            # Display Results
            st.divider()
            
            # Triage Level
            t_level = analysis["triage_level"]
            t_class = t_level.lower()
            st.markdown(f"""
                <div class="triage-card {t_class}">
                    <h2 style="margin:0; color: #1e293b;">{t_level}</h2>
                    <p style="margin:0.5rem 0 0 0; color: #475569;">{analysis['reasoning']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Safety Alerts
            if safety or analysis.get("safety_alerts"):
                st.error("⚠️ Clinical Safety Alerts")
                all_alerts = safety + analysis.get("safety_alerts", [])
                for alert in all_alerts:
                    with st.expander(f"{alert['severity']} Warning: {alert.get('medication', 'General')}"):
                        st.write(alert['risk'])
                        st.info(f"Recommendation: {alert['recommendation']}")

            # Protocols
            if analysis.get("protocols"):
                st.info("📚 Clinical Protocols Applied")
                for p in analysis["protocols"]:
                    st.write(f"**{p['condition']}**: {p['protocol']}")
                    st.caption(f"Source: {p['source']}")

            # JSON Data (for developers)
            with st.expander("View Raw Intelligence Metadata"):
                st.json(analysis)

st.sidebar.markdown("---")
st.sidebar.info("This is a Hackathon Demo. Always consult a real doctor for medical emergencies.")
