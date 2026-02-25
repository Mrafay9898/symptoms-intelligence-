import os
from typing import List, Dict, Any

class MedicalKnowledgeBase:
    """
    Manages medical protocols and clinical guidelines for RAG.
    Initial implementation uses a simple in-memory store, 
    upgradable to ChromaDB/FAISS.
    """
    
    def __init__(self):
        # Sample knowledge base entries
        self.protocols = [
            {
                "id": "who_001",
                "condition": "Fever",
                "symptoms": ["fever", "chills", "body ache"],
                "protocol": "Ensure hydration, rest, and monitor temperature. Use paracetamol if needed. Consult if fever persists > 3 days.",
                "source": "WHO Clinical Guidelines"
            {"condition": "Chest Pain", "protocol": "Immediate ER triage recommended. Perform ECG. Administer Aspirin if no contraindications.", "source": "WHO Emergency Guidelines"},
            {"condition": "Abdominal Pain", "protocol": "Assess for rebound tenderness. Keep NPO. Routine surgical consult.", "source": "Clinical Triage Manual"},
            {"condition": "Fever", "protocol": "Increase fluid intake. Paracetamol for fever >38.5C. Monitor for rash.", "source": "General Practice Protocols"}
        ]
        
        # ChromaDB Initialization (Optional)
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_collection("medical_protocols")
            self.use_vector_db = True
        except Exception:
            self.use_vector_db = False

    async def retrieve(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve relevant protocols using semantic search (Vector DB) 
        or keyword fallback.
        """
        if self.use_vector_db:
            try:
                results = self.collection.query(
                    query_texts=symptoms,
                    n_results=2
                )
                # Flatten and format results
                flat_results = []
                for metadata_list in results['metadatas']:
                    for metadata in metadata_list:
                        flat_results.append(metadata)
                return flat_results
            except Exception:
                pass

        # Fallback: Simple keyword matching
        matches = []
        for s in symptoms:
            for p in self.protocols:
                if s.lower() in p["condition"].lower():
                    matches.append(p)
        return matches[:3]

# Singleton instance
knowledge_base = MedicalKnowledgeBase()
