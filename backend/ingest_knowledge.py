import chromadb
from chromadb.utils import embedding_functions
import json
import os

# Initialize ChromaDB client
# In a real environment, this would be a persistent directory
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use a standard embedding function (OpenAI or similar)
# For hackathon demo, we can use a basic one or mock it if API keys are missing
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

def ingest_medical_protocols():
    collection = chroma_client.get_or_create_collection(
        name="medical_protocols",
        embedding_function=embedding_fn
    )

    # Sample expanded protocols
    protocols = [
        {
            "id": "p1",
            "condition": "Acute Chest Pain",
            "source": "WHO Emergency Care",
            "protocol": "Immediate ECG, oxygen if SpO2 < 94%, Aspirin 300mg. Triage to EMERGENCY.",
            "keywords": ["chest pain", "pressure", "shortness of breath", "radiating pain"]
        },
        {
            "id": "p2",
            "condition": "Severe Abdominal Pain",
            "source": "Clinical Triage Manual",
            "protocol": "NPO (Nothing by mouth), assess for surgical abdomen (rigidity/rebound). Triage to URGENT/EMERGENCY.",
            "keywords": ["stomach pain", "abdominal pain", "nausea", "vomiting"]
        },
        {
            "id": "p3",
            "condition": "High Fever",
            "source": "WHO Pediatrics",
            "protocol": "Check for neck stiffness/rash. Paracetamol for comfort. Hydration. Triage to ROUTINE/URGENT.",
            "keywords": ["fever", "chills", "high temperature"]
        }
    ]

    for p in protocols:
        collection.upsert(
            documents=[f"{p['condition']}: {p['protocol']}"],
            metadatas=[{"source": p["source"], "condition": p["condition"], "protocol": p["protocol"]}],
            ids=[p["id"]]
        )
    
    print(f"Ingested {len(protocols)} protocols into ChromaDB.")

if __name__ == "__main__":
    ingest_medical_protocols()
