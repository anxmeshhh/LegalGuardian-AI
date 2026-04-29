"""
LegalGuardian AI — Role-Aware Risk Scoring Engine

Scores clauses based on:
1. Inherent clause type risk (from CUAD risk mappings)
2. Role-specific risk modifiers (same clause = different risk for different parties)
3. Textual risk indicators (specific words/phrases that amplify risk)
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


# Textual risk amplifiers — words/phrases that increase risk regardless of clause type
RISK_AMPLIFIERS = {
    "high": [
        "unlimited", "uncapped", "irrevocable", "perpetual", "sole discretion",
        "without limitation", "indemnify and hold harmless", "waive all rights",
        "at any time without notice", "without cause", "no liability whatsoever",
        "shall not exceed zero", "entire liability", "forfeit",
        "immediately terminate", "in its sole and absolute discretion",
        "unconditionally", "notwithstanding anything to the contrary"
    ],
    "medium": [
        "reasonable efforts", "best efforts", "material breach",
        "automatically renew", "auto-renewal", "survive termination",
        "at its discretion", "may terminate", "liquidated damages",
        "binding arbitration", "waive.*jury trial", "non-compete",
        "non-solicitation", "confidential.*perpetuity"
    ],
    "low": [
        "mutual", "both parties", "reasonable", "good faith",
        "written consent", "prior notice", "cure period",
        "thirty (30) days", "sixty (60) days"
    ]
}

# Risk reduction indicators
RISK_REDUCERS = [
    "mutual", "both parties equally", "reciprocal",
    "reasonable", "good faith", "best efforts",
    "with prior written consent", "subject to applicable law",
    "to the extent permitted by law"
]


class RiskScorer:
    """
    Computes role-aware risk scores for legal clauses.
    
    Risk score range: 0 (safe) to 100 (extremely risky)
    Risk levels: LOW (0-39), MEDIUM (40-69), HIGH (70-100)
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = str(Path(__file__).resolve().parent.parent / "data")
        
        self.data_dir = Path(data_dir)
        self.risk_mappings = self._load_json("risk_mappings.json")
    
    def _load_json(self, filename: str) -> dict:
        """Load a JSON data file."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def score_clause(self, clause_text: str, clause_type: str, 
                     role: str, doc_type: str = "") -> Dict:
        """
        Compute risk score for a single clause.
        
        Args:
            clause_text: The clause text
            clause_type: Classified clause type (from ClauseClassifier)
            role: User's role (e.g., 'employee', 'tenant')
            doc_type: Document type (e.g., 'employment_contract')
        
        Returns:
            Dict with risk_level, risk_score, risk_factors, and is_one_sided
        """
        # Step 1: Get base risk from clause type mapping
        base_risk = self._get_base_risk(clause_type)
        
        # Step 2: Apply role-specific modifier
        role_risk = self._get_role_risk(clause_type, role)
        
        # Step 3: Analyze text for risk amplifiers/reducers
        text_analysis = self._analyze_text_risk(clause_text)
        
        # Step 4: Detect one-sidedness
        is_one_sided = self._detect_one_sidedness(clause_text)
        
        # Step 5: Compute final score
        # Base score from risk level
        risk_scores = {"HIGH": 80, "MEDIUM": 50, "LOW": 20}
        
        # Use role risk if available, otherwise base risk
        effective_risk = role_risk if role_risk else base_risk
        base_score = risk_scores.get(effective_risk, 50)
        
        # Adjust based on text analysis
        score = base_score
        score += text_analysis["amplifier_boost"]
        score -= text_analysis["reducer_discount"]
        
        # One-sided clauses get a boost
        if is_one_sided:
            score += 10
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine final risk level
        if score >= 70:
            risk_level = "HIGH"
        elif score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": round(score),
            "base_risk": base_risk,
            "role_adjusted_risk": effective_risk,
            "risk_factors": text_analysis["factors"],
            "is_one_sided": is_one_sided,
            "attention_words": text_analysis["attention_words"]
        }
    
    def _get_base_risk(self, clause_type: str) -> str:
        """Get default risk level for a clause type."""
        mappings = self.risk_mappings.get("clause_type_to_risk", {})
        entry = mappings.get(clause_type, {})
        return entry.get("default", "MEDIUM")
    
    def _get_role_risk(self, clause_type: str, role: str) -> Optional[str]:
        """Get role-specific risk level for a clause type."""
        modifiers = self.risk_mappings.get("role_risk_modifiers", {})
        role_mods = modifiers.get(role, {})
        return role_mods.get(clause_type)
    
    def _analyze_text_risk(self, text: str) -> Dict:
        """Analyze clause text for risk amplifiers and reducers."""
        text_lower = text.lower()
        factors = []
        attention_words = []
        amplifier_boost = 0
        reducer_discount = 0
        
        # Check amplifiers
        for level, phrases in RISK_AMPLIFIERS.items():
            for phrase in phrases:
                if '.*' in phrase:
                    match = re.search(phrase, text_lower)
                    if match:
                        matched_text = match.group(0)
                        attention_words.append(matched_text)
                        if level == "high":
                            amplifier_boost += 8
                            factors.append(f"Contains high-risk language: '{matched_text}'")
                        elif level == "medium":
                            amplifier_boost += 4
                            factors.append(f"Contains cautionary language: '{matched_text}'")
                elif phrase in text_lower:
                    attention_words.append(phrase)
                    if level == "high":
                        amplifier_boost += 8
                        factors.append(f"Contains high-risk language: '{phrase}'")
                    elif level == "medium":
                        amplifier_boost += 4
                        factors.append(f"Contains cautionary language: '{phrase}'")
        
        # Check reducers
        for phrase in RISK_REDUCERS:
            if phrase in text_lower:
                reducer_discount += 5
                factors.append(f"Contains protective language: '{phrase}'")
        
        # Cap adjustments
        amplifier_boost = min(amplifier_boost, 25)
        reducer_discount = min(reducer_discount, 15)
        
        return {
            "amplifier_boost": amplifier_boost,
            "reducer_discount": reducer_discount,
            "factors": factors,
            "attention_words": list(set(attention_words))[:10]  # Dedupe, limit
        }
    
    def _detect_one_sidedness(self, text: str) -> bool:
        """Detect if a clause is one-sided (favors one party disproportionately)."""
        text_lower = text.lower()
        
        one_sided_patterns = [
            r"(?:employer|landlord|client|lender|platform|insurer)\s+may\s+terminate.*(?:employee|tenant|provider|borrower|user|policyholder)\s+(?:may not|cannot|shall not)",
            r"sole discretion",
            r"at any time.*without.*(?:notice|cause|reason)",
            r"(?:shall|will)\s+not\s+exceed\s+(?:zero|nil|\$0)",
            r"waive.*(?:all|any).*right",
            r"regardless of.*negligence",
        ]
        
        for pattern in one_sided_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def compute_document_risk(self, clause_risks: List[Dict]) -> Dict:
        """
        Compute aggregate risk score for the entire document.
        
        Args:
            clause_risks: List of individual clause risk results
        
        Returns:
            Document-level risk summary
        """
        if not clause_risks:
            return {
                "overall_risk_score": 0,
                "overall_risk_level": "LOW",
                "risk_breakdown": {"high": 0, "medium": 0, "low": 0},
                "total_clauses": 0,
                "highest_risk_clauses": []
            }
        
        scores = [cr["risk_score"] for cr in clause_risks]
        levels = [cr["risk_level"] for cr in clause_risks]
        
        risk_breakdown = {
            "high": levels.count("HIGH"),
            "medium": levels.count("MEDIUM"),
            "low": levels.count("LOW")
        }
        
        # Overall score: weighted average favoring high-risk clauses
        # High-risk clauses contribute more to overall score
        weighted_sum = 0
        weight_total = 0
        for cr in clause_risks:
            weight = 3.0 if cr["risk_level"] == "HIGH" else (1.5 if cr["risk_level"] == "MEDIUM" else 1.0)
            weighted_sum += cr["risk_score"] * weight
            weight_total += weight
        
        overall_score = round(weighted_sum / weight_total) if weight_total > 0 else 0
        
        if overall_score >= 70:
            overall_level = "HIGH"
        elif overall_score >= 40:
            overall_level = "MEDIUM"
        else:
            overall_level = "LOW"
        
        # Top risk clauses
        sorted_risks = sorted(
            enumerate(clause_risks), 
            key=lambda x: x[1]["risk_score"], 
            reverse=True
        )
        highest_risk = [{"index": i, **cr} for i, cr in sorted_risks[:5]]
        
        return {
            "overall_risk_score": overall_score,
            "overall_risk_level": overall_level,
            "risk_breakdown": risk_breakdown,
            "total_clauses": len(clause_risks),
            "highest_risk_clauses": highest_risk
        }


# Module-level instance
_scorer_instance = None

def get_risk_scorer(data_dir: Optional[str] = None) -> RiskScorer:
    """Get or create the risk scorer singleton."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = RiskScorer(data_dir)
    return _scorer_instance
