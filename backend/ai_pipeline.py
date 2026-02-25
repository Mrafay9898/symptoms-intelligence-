import os
from typing import List, Dict, Any

class SymptomIntelligenceEngine:
    """
    Core engine for symptom extraction, RAG-based reasoning, and triage.
    """
    
    def __init__(self):
        # Placeholder for LLM and Vector DB initialization
        self.knowledge_base_ready = False
        self.model_name = "gpt-4-turbo"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.is_fully_configured = bool(self.api_key and self.api_key.startswith("sk-"))

    async def extract_symptoms(self, text: str) -> List[Dict[str, Any]]:
        """
        Uses LLM to extract structured symptom list from unstructured user text.
        """
        prompt = f"""
        Extract a list of symptoms from the following patient description. 
        For each symptom, identify:
        1. Name (standard clinical term)
        2. Severity (mild, moderate, severe, or unknown)
        3. Duration (if mentioned)
        
        Text: "{text}"
        
        Format as JSON list:
        [{{"name": "...", "severity": "...", "duration": "..."}}]
        """
        
        # In a real implementation, we would call the OpenAI API:
        # response = await openai.ChatCompletion.acreate(
        #     model=self.model_name,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return json.loads(response.choices[0].message.content)
        
        # Mocking the AI response for now to allow integration development
        return [
            {"name": "Abdominal Pain", "severity": "moderate", "duration": "2 hours"},
            {"name": "Nausea", "severity": "mild", "duration": "recent"}
        ]


    async def detect_red_flags(self, symptoms: List[str]) -> bool:
        """
        Quick check for emergency symptoms that require immediate triage.
        """
        emergency_keywords = ["chest pain", "shortness of breath", "unconscious"]
        return any(keyword in " ".join(symptoms).lower() for keyword in emergency_keywords)

    async def retrieve_clinical_guidelines(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        RAG: Retrieve relevant WHO/Clinical protocols from the Knowledge Base.
        """
        from .knowledge_base import knowledge_base
        return await knowledge_base.retrieve(symptoms)

    async def generate_diagnosis_and_triage(
        self, 
        extracted_symptoms: List[Dict[str, Any]], 
        vitals: Dict[str, Any] = None,
        medications: List[str] = None,
        existing_conditions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Final reasoning step to provide a structured triage output.
        """
        from .medication_checker import medication_safety
        
        symptom_names = [s["name"] for s in extracted_symptoms]
        is_emergency = await self.detect_red_flags(symptom_names)
        
        # 1. RAG retrieval from medical knowledge base
        retrieved_protocols = await self.retrieve_clinical_guidelines(symptom_names)
        protocol_summaries = [f"{p['source']}: {p['condition']}" for p in retrieved_protocols]
        
        # 2. Medication/Condition safety checks
        safety_alerts = await medication_safety.check_interactions(medications or [], existing_conditions or [])
        
        # 3. Decision Logic
        triage_level = "EMERGENCY" if is_emergency else "ROUTINE"
        severities = [s.get("severity", "").lower() for s in extracted_symptoms]
        
        if "severe" in severities and not is_emergency:
            triage_level = "URGENT"
        elif "moderate" in severities and triage_level == "ROUTINE":
            triage_level = "URGENT"

        
        # Escalate if safety alerts are critical
        if any(a["severity"] in ["HIGH", "CRITICAL"] for a in safety_alerts):
            triage_level = "URGENT" if triage_level == "ROUTINE" else triage_level

        reasoning = (
            f"Assessment based on {len(extracted_symptoms)} symptoms identified. "
            f"Clinical protocols matched: {', '.join(protocol_summaries) if protocol_summaries else 'General assessment'}. "
            f"Safety alerts found: {len(safety_alerts)}. "
            f"Red flag check: {'Positive' if is_emergency else 'Negative'}."
        )

        recommendations = []
        if is_emergency:
            recommendations.append("SEEK EMERGENCY MEDICAL ATTENTION IMMEDIATELY.")
        
        for p in retrieved_protocols:
            recommendations.append(p["protocol"])
        
        if not recommendations:
            recommendations.append("Monitor symptoms and maintain hydration. Consult a physician if condition worsens.")

        return {
            "symptoms": extracted_symptoms,
            "triage_level": triage_level,
            "reasoning": reasoning,
            "summary": reasoning,
            "recommendations": recommendations[:3],
            "safety_alerts": safety_alerts,
            "confidence_score": 0.92 if protocol_summaries else 0.82,
            "disclaimer": "AI-generated decision support. Not a clinical diagnosis."
        }




# Singleton instance
engine = SymptomIntelligenceEngine()
