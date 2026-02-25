from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import SymptomRequest, AnalysisResponse

app = FastAPI(
    title="Symptom Intelligence Engine API",
    description="AI-driven clinical decision support system backend.",
    version="0.1.0"
)

# CORS configuration
origins = [
    "http://localhost:5173",
    "https://*.render.com",
    "https://symptoms-intelligence.onrender.com", # Placeholder for user's eventual domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon convenience, ideally restricted in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Symptom Intelligence Engine API",
        "version": "0.1.0"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_symptoms(request: SymptomRequest):
    """
    Endpoint for the AI Analysis pipeline.
    Uses Pydantic schemas for request validation and response formatting.
    """
    from .ai_pipeline import engine
    
    # 1. Extract symptoms from text
    symptoms = await engine.extract_symptoms(request.text)
    
    # 2. Run triage and reasoning with safety checks
    analysis = await engine.generate_diagnosis_and_triage(
        symptoms, 
        request.vitals,
        request.medications,
        request.existing_conditions
    )
    
    return analysis




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
