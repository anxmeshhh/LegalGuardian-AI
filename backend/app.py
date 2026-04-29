"""
LegalGuardian AI — FastAPI Backend Application

Main API server that orchestrates the NLP pipeline:
Input → Preprocess → Classify → Score → Explain → Recommend → Output
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

from .config import DOCUMENT_TYPES, CORS_ORIGINS, API_HOST, API_PORT
from .services.preprocessor import extract_text, segment_clauses
from .models.clause_classifier import get_classifier
from .models.risk_scorer import get_risk_scorer
from .services.explainer import get_explainer
from .services.recommender import get_recommender

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LegalGuardian AI",
    description="NLP-Powered Legal Contract Risk Analysis & Decision-Support System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ─── Request / Response Models ────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    contract_text: str
    document_type: str = "other"
    user_role: str = "general"

class QARequest(BaseModel):
    contract_text: str
    question: str


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the frontend application."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "LegalGuardian AI API is running. Frontend not found."}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LegalGuardian AI"}


@app.get("/api/doc-types")
async def get_document_types():
    """Return available document types and role options."""
    return {"document_types": DOCUMENT_TYPES}


@app.post("/api/analyze")
async def analyze_contract(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    
    Accepts document type, user role, and contract text.
    Returns full risk report with clause-level analysis.
    """
    if not request.contract_text or len(request.contract_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Contract text is too short. Please provide at least 50 characters."
        )
    
    # Initialize components
    classifier = get_classifier()
    scorer = get_risk_scorer()
    explainer = get_explainer()
    recommender = get_recommender()
    
    # Step 1: Clean and segment the contract
    clean_text_content = extract_text(request.contract_text)
    clauses = segment_clauses(clean_text_content)
    
    if not clauses:
        raise HTTPException(
            status_code=400,
            detail="Could not segment the contract into clauses. Please check the format."
        )
    
    # Step 2: Analyze each clause
    analyzed_clauses = []
    clause_risks = []
    
    for clause in clauses:
        # Classify
        classification = classifier.classify(clause["text"])
        
        # Score risk
        risk = scorer.score_clause(
            clause_text=clause["text"],
            clause_type=classification["clause_type"],
            role=request.user_role,
            doc_type=request.document_type
        )
        
        # Generate explanation
        explanation = explainer.explain_clause(
            clause_text=clause["text"],
            clause_type=classification["clause_type"],
            role=request.user_role,
            risk_level=risk["risk_level"]
        )
        
        # Get recommendations
        recs = recommender.get_recommendations(
            clause_type=classification["clause_type"],
            risk_level=risk["risk_level"],
            role=request.user_role
        )
        
        analyzed_clause = {
            "id": clause["id"],
            "title": clause["title"],
            "text": clause["text"],
            "clause_type": classification["clause_type"],
            "classification_confidence": classification["confidence"],
            "classification_method": classification["method"],
            "risk_level": risk["risk_level"],
            "risk_score": risk["risk_score"],
            "is_one_sided": risk["is_one_sided"],
            "risk_factors": risk["risk_factors"],
            "attention_words": risk["attention_words"],
            "explanation": explanation["explanation"],
            "role_impact": explanation["role_impact"],
            "summary": explanation["summary"],
            "key_terms": explanation["key_terms"],
            "recommendations": recs
        }
        
        analyzed_clauses.append(analyzed_clause)
        clause_risks.append(risk)
    
    # Step 3: Compute document-level risk
    doc_risk = scorer.compute_document_risk(clause_risks)
    
    # Step 4: Get document-level recommendations
    doc_recs = recommender.get_document_recommendations(
        [{"clause_type": c["clause_type"], "risk_level": c["risk_level"]} 
         for c in analyzed_clauses]
    )
    
    # Step 5: Build response
    response = {
        "document_summary": {
            "total_clauses": doc_risk["total_clauses"],
            "risk_breakdown": doc_risk["risk_breakdown"],
            "overall_risk_score": doc_risk["overall_risk_score"],
            "overall_risk_level": doc_risk["overall_risk_level"],
            "document_type": DOCUMENT_TYPES.get(request.document_type, {}).get("label", "Unknown"),
            "user_role": request.user_role,
            "document_recommendations": doc_recs
        },
        "clauses": analyzed_clauses,
        "disclaimer": "⚖️ This analysis is for informational purposes only and does not constitute legal advice. Always consult a qualified attorney for legal matters."
    }
    
    return response


@app.post("/api/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    user_role: str = Form("general")
):
    """Analyze an uploaded contract file (PDF, DOCX, or TXT)."""
    # Validate file type
    allowed_types = [
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    
    content = await file.read()
    
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    
    # Extract text from file
    try:
        text = extract_text("", file_bytes=content, file_type=file.content_type or file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Use the text analysis endpoint
    request = AnalyzeRequest(
        contract_text=text,
        document_type=document_type,
        user_role=user_role
    )
    return await analyze_contract(request)


@app.post("/api/qa")
async def question_answer(request: QARequest):
    """Answer a question about the contract."""
    if not request.contract_text or not request.question:
        raise HTTPException(
            status_code=400,
            detail="Both contract text and question are required."
        )
    
    try:
        from .models.qa_model import get_qa_model
        qa = get_qa_model()
        result = qa.answer(request.question, request.contract_text)
        return result
    except Exception as e:
        # Fallback: return a helpful message
        return {
            "answer": f"QA model is not available. Error: {str(e)}. Please ensure transformers library is installed.",
            "confidence": 0.0,
            "method": "error"
        }


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
