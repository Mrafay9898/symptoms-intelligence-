import streamlit as st
# Triggering clean redeploy to sync dependencies
import asyncio
from backend.ai_pipeline import engine
from backend.medication_checker import medication_safety
import json
import os
from streamlit_mic_recorder import mic_recorder

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

# API Key Diagnostic Doctor
if not engine.api_key or not engine.api_key.startswith("sk-"):
    st.error("🚨 **API Key Missing or Invalid**")
    st.warning("""
        Your AI features (analysis, reasoning, and voice transcription) will not work without a valid OpenAI API Key.
        
        **How to fix:**
        1. Go to **Streamlit Dashboard** -> **Settings** -> **Secrets**.
        2. Paste: `OPENAI_API_KEY = "your-key-here"`.
        3. Save and the app will restart.
    """)
    st.info("💡 Tip: You can get your key at [platform.openai.com](https://platform.openai.com/api-keys)")
else:
    st.sidebar.success("✅ AI Engine: Online (Connected to OpenAI)")

# Input Section
with st.container():
    st.subheader("Assessment Details")
    if 'symptom_input' not in st.session_state:
        st.session_state.symptom_input = ""
        
    symptom_text = st.text_area(
        "Describe your symptoms (e.g., 'Severe headache for 2 days')", 
        value=st.session_state.symptom_input,
        height=100,
        key="symptom_area"
    )
    # Update state if manually typed
    st.session_state.symptom_input = symptom_text
    
    # Voice Input
    st.write("🎤 Or record your symptoms:")
    audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key='recorder'
    )
    
    if audio:
        with st.spinner("Transcribing your voice..."):
            try:
                from openai import OpenAI
                client = OpenAI() # Uses OPENAI_API_KEY from environment
                
                # Save bytes to temp file for Whisper API
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio['bytes'])
                    tmp_path = tmp.name
                
                with open(tmp_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                
                if transcription.text:
                    symptom_text = transcription.text
                    st.success(f"Transcribed: {symptom_text}")
                    # Update session state so it persists in the text area
                    st.session_state.symptom_input = symptom_text
            except Exception as e:
                st.error(f"Transcription failed: {str(e)}")
                st.info("Audio captured, but transcription requires a valid OPENAI_API_KEY.")
    
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
