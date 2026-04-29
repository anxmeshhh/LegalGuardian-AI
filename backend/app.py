"""
LegalGuardian AI — Flask Backend Application

Main API server that orchestrates the NLP pipeline:
Input → Preprocess → Classify → Score → Explain → Recommend → Output
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os

from .config import DOCUMENT_TYPES, API_HOST, API_PORT
from .services.preprocessor import extract_text, segment_clauses
from .models.clause_classifier import get_classifier
from .models.risk_scorer import get_risk_scorer
from .services.explainer import get_explainer
from .services.recommender import get_recommender

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ─── Frontend Serving ─────────────────────────────────────────────────────────

@app.route("/")
def serve_frontend():
    """Serve the main HTML page."""
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/css/<path:filename>")
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory(str(FRONTEND_DIR / "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory(str(FRONTEND_DIR / "js"), filename)


# ─── Shared Pipeline Logic ───────────────────────────────────────────────────

def _run_pipeline(contract_text: str, document_type: str, user_role: str) -> dict:
    """
    Execute the full NLP analysis pipeline.
    
    This is the core engine shared by both /api/analyze and /api/analyze-file.
    Returns the complete analysis response dict, or raises ValueError on bad input.
    """
    if not contract_text or len(contract_text) < 50:
        raise ValueError("Contract text is too short. Please provide at least 50 characters.")
    
    # Initialize components
    classifier = get_classifier()
    scorer = get_risk_scorer()
    explainer = get_explainer()
    recommender = get_recommender()
    
    # Step 1: Clean and segment the contract
    clean_text_content = extract_text(contract_text)
    clauses = segment_clauses(clean_text_content)
    
    if not clauses:
        raise ValueError("Could not segment the contract into clauses. Please check the format.")
    
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
            role=user_role,
            doc_type=document_type
        )
        
        # Generate explanation
        explanation = explainer.explain_clause(
            clause_text=clause["text"],
            clause_type=classification["clause_type"],
            role=user_role,
            risk_level=risk["risk_level"]
        )
        
        # Get recommendations
        recs = recommender.get_recommendations(
            clause_type=classification["clause_type"],
            risk_level=risk["risk_level"],
            role=user_role
        )
        
        analyzed_clauses.append({
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
        })
        clause_risks.append(risk)
    
    # Step 3: Compute document-level risk
    doc_risk = scorer.compute_document_risk(clause_risks)
    
    # Step 4: Get document-level recommendations
    doc_recs = recommender.get_document_recommendations(
        [{"clause_type": c["clause_type"], "risk_level": c["risk_level"]}
         for c in analyzed_clauses]
    )
    
    # Step 5: Build response
    return {
        "document_summary": {
            "total_clauses": doc_risk["total_clauses"],
            "risk_breakdown": doc_risk["risk_breakdown"],
            "overall_risk_score": doc_risk["overall_risk_score"],
            "overall_risk_level": doc_risk["overall_risk_level"],
            "document_type": DOCUMENT_TYPES.get(document_type, {}).get("label", "Unknown"),
            "user_role": user_role,
            "document_recommendations": doc_recs
        },
        "clauses": analyzed_clauses,
        "disclaimer": "⚖️ This analysis is for informational purposes only and does not constitute legal advice. Always consult a qualified attorney for legal matters."
    }


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "LegalGuardian AI"})


@app.route("/api/doc-types", methods=["GET"])
def get_document_types():
    """Return available document types and role options."""
    return jsonify({"document_types": DOCUMENT_TYPES})


@app.route("/api/analyze", methods=["POST"])
def analyze_contract():
    """
    Main analysis endpoint.
    Accepts JSON with contract_text, document_type, user_role.
    """
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required."}), 400
    
    try:
        result = _run_pipeline(
            contract_text=data.get("contract_text", "").strip(),
            document_type=data.get("document_type", "other"),
            user_role=data.get("user_role", "general")
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400


@app.route("/api/analyze-file", methods=["POST"])
def analyze_file():
    """Analyze an uploaded contract file (PDF, DOCX, or TXT)."""
    if "file" not in request.files:
        return jsonify({"detail": "No file uploaded."}), 400
    
    file = request.files["file"]
    document_type = request.form.get("document_type", "other")
    user_role = request.form.get("user_role", "general")
    
    content = file.read()
    if not content:
        return jsonify({"detail": "Empty file uploaded."}), 400
    
    # Extract text from file
    try:
        text = extract_text("", file_bytes=content, file_type=file.content_type or file.filename)
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    
    # Run through the shared pipeline
    try:
        result = _run_pipeline(
            contract_text=text,
            document_type=document_type,
            user_role=user_role
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400


@app.route("/api/qa", methods=["POST"])
def question_answer():
    """Answer a question about the contract."""
    data = request.get_json()
    
    if not data:
        return jsonify({"detail": "Request body is required."}), 400
    
    contract_text = data.get("contract_text", "")
    question = data.get("question", "")
    
    if not contract_text or not question:
        return jsonify({"detail": "Both contract text and question are required."}), 400
    
    try:
        from .models.qa_model import get_qa_model
        qa = get_qa_model()
        result = qa.answer(question, contract_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "answer": f"QA model encountered an issue: {str(e)}. Using keyword-based search.",
            "confidence": 0.0,
            "method": "error"
        })


# ─── Entry Point ──────────────────────────────────────────────────────────────

def create_app():
    """Application factory for production use."""
    return app


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT, debug=True)
