from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SymptomRequest(BaseModel):
    """
    Schema for incoming symptom analysis requests.
    """
    text: str = Field(..., description="Unstructured symptom description from the user.")
    vitals: Optional[Dict[str, Any]] = Field(None, description="Optional vital signs like temperature, heart rate.")
    medications: List[str] = Field(default=[], description="List of medications the user is currently taking.")
    existing_conditions: List[str] = Field(default=[], description="Existing medical conditions.")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Optional demographic or historical data.")

class SymptomAnalysis(BaseModel):
    """
    Schema for a single analyzed symptom.
    """
    name: str = Field(..., description="Normalized name of the symptom.")
    severity: str = Field("unknown", description="Extracted severity (mild, moderate, severe).")
    duration: Optional[str] = Field(None, description="Extracted duration.")

class AnalysisResponse(BaseModel):
    """
    Schema for the final AI analysis and triage response.
    """
    symptoms: List[SymptomAnalysis] = Field(..., description="List of structured symptoms extracted.")
    triage_level: str = Field(..., description="Triage category (EMERGENCY, URGENT, ROUTINE, SELF_CARE).")
    reasoning: str = Field(..., description="Explainable AI reasoning for the assessment.")
    recommendations: List[str] = Field(..., description="Immediate next steps or clinical protocol advice.")
    safety_alerts: List[Dict[str, Any]] = Field(default=[], description="Critical safety warnings regarding medications or conditions.")
    confidence_score: float = Field(..., description="AI confidence in the assessment (0.0 to 1.0).")
    disclaimer: str = Field(
        default="This is an AI-generated assessment for decision support and not a clinical diagnosis. Consult a professional."
    )
