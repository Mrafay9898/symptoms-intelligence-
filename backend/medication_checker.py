from typing import List, Dict, Any

class MedicationSafetyChecker:
    """
    Checks for common hazardous interactions between medications and symptoms.
    Focuses on hackathon prototype safety rules.
    """
    
    def __init__(self):
        # Sample interaction database
        self.interactions = [
            {
                "med_a": "Aspirin",
                "med_b": "Ibuprofen",
                "risk": "Increased risk of stomach ulcers and bleeding",
                "severity": "HIGH"
            },
            {
                "med_a": "Warfarin",
                "med_b": "Aspirin",
                "risk": "High risk of excessive bleeding",
                "severity": "CRITICAL"
            }
        ]
        
        self.condition_contraindications = [
            {
                "med": "Ibuprofen",
                "condition": "Asthma",
                "risk": "May trigger asthma attacks (NSAID sensitivity)",
                "severity": "MODERATE"
            },
            {
                "med": "Warfarin",
                "condition": "Ulcer",
                "risk": "Risk of internal bleeding",
                "severity": "CRITICAL"
            }
        ]

    async def check_interactions(self, medications: List[str], existing_conditions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Checks for interaction risks among a list of medications and conditions.
        """
        alerts = []
        meds_normalized = [m.strip().capitalize() for m in medications]
        conditions_normalized = [c.strip().capitalize() for c in (existing_conditions or [])]
        
        # Check drug-drug interactions
        for i, med_a in enumerate(meds_normalized):
            for med_b in meds_normalized[i+1:]:
                for interaction in self.interactions:
                    if (med_a == interaction["med_a"] and med_b == interaction["med_b"]) or \
                       (med_a == interaction["med_b"] and med_b == interaction["med_a"]):
                        alerts.append(interaction)
        
        # Check drug-condition contraindications
        for med in meds_normalized:
            for contra in self.condition_contraindications:
                if med == contra["med"]:
                    # Check if any identified condition matches
                    for condition in conditions_normalized:
                        if condition.lower() in contra["condition"].lower():
                            alerts.append(contra)
                            
        return alerts

# Singleton instance
medication_safety = MedicationSafetyChecker()
