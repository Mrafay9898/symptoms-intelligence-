import pytest
from ai_pipeline import engine
from medication_checker import medication_safety

@pytest.mark.asyncio
async def test_red_flag_detection():
    # Test case: Chest pain should trigger red flag
    is_emergency = await engine.detect_red_flags(["chest pain", "headache"])
    assert is_emergency is True

    # Test case: General symptoms should not trigger red flag
    is_emergency = await engine.detect_red_flags(["cough", "fever"])
    assert is_emergency is False

@pytest.mark.asyncio
async def test_medication_interaction():
    # Test case: Warfarin + Aspirin interaction
    alerts = await medication_safety.check_interactions(["Warfarin", "Aspirin"], [])
    assert any("risk of bleeding" in a["risk"].lower() for a in alerts)
    assert any(a["severity"] == "HIGH" for a in alerts)

@pytest.mark.asyncio
async def test_triage_escalation():
    # Test case: High severity symptoms should escalate triage
    analysis = await engine.generate_diagnosis_and_triage(
        extracted_symptoms=[{"name": "Stomach Pain", "severity": "severe", "duration": "2h"}],
        medications=[],
        existing_conditions=[]
    )
    # Severe symptoms with red flags (if keywords matched) or just internal logic
    # In my logic, 'severe' symptoms aren't matching 'moderate' for URGENT, let's check
    # My logic: triage_level = "EMERGENCY" if is_emergency else "ROUTINE"
    # if "moderate" in [s.get("severity", "") for s in extracted_symptoms] and not is_emergency:
    #     triage_level = "URGENT"
    # Wait, 'severe' should probably escalate too.
    assert analysis["triage_level"] in ["URGENT", "EMERGENCY"]

@pytest.mark.asyncio
async def test_condition_contraindication():
    # Test case: Ibuprofen + Asthma
    alerts = await medication_safety.check_interactions(["Ibuprofen"], ["Asthma"])
    assert any("bronchospasm" in a["risk"].lower() for a in alerts)
