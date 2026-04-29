"""
LegalGuardian AI — Plain-English Explanation Generator

Generates role-aware, plain-English explanations for legal clauses.
Uses:
1. Legal dictionary for term-level translations
2. Role templates for personalized framing
3. Pattern-based explanation generation
"""

import json
import re
from typing import Dict, List, Optional
from pathlib import Path


class Explainer:
    """
    Generates plain-English explanations for legal clauses,
    personalized to the user's role.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = str(Path(__file__).resolve().parent.parent / "data")
        
        self.data_dir = Path(data_dir)
        self.legal_dictionary = self._load_json("legal_dictionary.json").get("terms", {})
        self.role_templates = self._load_json("role_templates.json").get("role_templates", {})
    
    def _load_json(self, filename: str) -> dict:
        """Load a JSON data file."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def explain_clause(self, clause_text: str, clause_type: str,
                       role: str, risk_level: str = "MEDIUM") -> Dict:
        """
        Generate a plain-English explanation for a clause.
        
        Args:
            clause_text: The clause text
            clause_type: Classified clause type
            role: User's role
            risk_level: Risk level (HIGH/MEDIUM/LOW)
        
        Returns:
            Dict with 'explanation', 'role_impact', 'key_terms', 'summary'
        """
        # Step 1: Get role-specific framing
        role_impact = self._get_role_impact(clause_type, role)
        
        # Step 2: Find and explain key legal terms
        key_terms = self._find_key_terms(clause_text)
        
        # Step 3: Generate the explanation
        explanation = self._generate_explanation(
            clause_text, clause_type, role, risk_level, role_impact
        )
        
        # Step 4: Create one-line summary
        summary = self._generate_summary(clause_type, role, risk_level)
        
        return {
            "explanation": explanation,
            "role_impact": role_impact,
            "key_terms": key_terms,
            "summary": summary
        }
    
    def _get_role_impact(self, clause_type: str, role: str) -> str:
        """Get role-specific impact statement for a clause type."""
        role_data = self.role_templates.get(role, {})
        clause_frames = role_data.get("clause_frames", {})
        
        if clause_type in clause_frames:
            return clause_frames[clause_type]
        
        # Generate a generic role-aware impact
        perspective = role_data.get("perspective", "From your perspective")
        vulnerability = role_data.get("vulnerability", "review this clause carefully")
        
        return f"{perspective}, {vulnerability}. This {clause_type.lower()} clause should be reviewed carefully."
    
    def _find_key_terms(self, clause_text: str) -> List[Dict]:
        """Find legal terms in the clause and provide definitions."""
        found_terms = []
        text_lower = clause_text.lower()
        
        for term, details in self.legal_dictionary.items():
            if term.lower() in text_lower:
                found_terms.append({
                    "term": term,
                    "definition": details.get("definition", ""),
                    "plain_english": details.get("plain_english", ""),
                    "risk_note": details.get("risk_note", "")
                })
        
        return found_terms
    
    def _generate_explanation(self, clause_text: str, clause_type: str,
                              role: str, risk_level: str,
                              role_impact: str) -> str:
        """Generate a comprehensive plain-English explanation."""
        role_data = self.role_templates.get(role, {})
        perspective = role_data.get("perspective", "In general")
        
        # Risk-level prefix
        risk_prefix = {
            "HIGH": "⚠️ **HIGH RISK** — This clause requires immediate attention.",
            "MEDIUM": "🟡 **MEDIUM RISK** — This clause has some concerns worth reviewing.",
            "LOW": "🟢 **LOW RISK** — This is a standard clause with minimal concern."
        }
        
        parts = []
        
        # 1. Risk prefix
        parts.append(risk_prefix.get(risk_level, ""))
        
        # 2. What this clause does
        clause_description = self._describe_clause_type(clause_type)
        if clause_description:
            parts.append(f"\n\n**What this means:** {clause_description}")
        
        # 3. Role-specific impact
        if role_impact:
            parts.append(f"\n\n**Impact on you:** {role_impact}")
        
        # 4. Specific concerns from the text
        concerns = self._extract_specific_concerns(clause_text, clause_type)
        if concerns:
            parts.append("\n\n**Key concerns in this clause:**")
            for concern in concerns:
                parts.append(f"\n• {concern}")
        
        return "".join(parts)
    
    def _describe_clause_type(self, clause_type: str) -> str:
        """Get a plain-English description of what a clause type means."""
        descriptions = {
            "Indemnification": "This clause determines who pays when things go wrong. It creates an obligation for one party to compensate the other for losses, damages, or legal costs.",
            "Uncapped Liability": "This clause means there is NO maximum limit on how much money one party could owe. Financial exposure is potentially infinite.",
            "Cap On Liability": "This clause sets a maximum limit on how much one party can be held financially responsible for. The cap amount is critical — check if it's reasonable.",
            "Non-Compete": "This clause restricts your ability to work for competitors or start a competing business after the contract ends. It directly affects your career and income.",
            "Exclusivity": "This clause requires you to work exclusively with this party, preventing you from taking on other clients or partners in the same area.",
            "Termination For Convenience": "This allows one or both parties to end the contract at any time without needing a specific reason. Check if this right is mutual.",
            "Ip Ownership Assignment": "This clause transfers intellectual property rights (inventions, code, designs, creative work) from one party to another. Extremely important for creators.",
            "Confidentiality": "This clause requires keeping certain information secret. Check the scope (what's covered) and duration (how long it lasts).",
            "Renewal Term": "This clause governs how the contract renews. Auto-renewal means the contract extends automatically unless you actively cancel before the deadline.",
            "Notice Period To Terminate Renewal": "This specifies how far in advance you must notify the other party if you don't want to renew. Missing this window traps you in another term.",
            "Liquidated Damages": "This sets a pre-determined penalty amount for specific breaches. The amount is decided upfront, not by a court.",
            "Governing Law": "This determines which jurisdiction's laws apply to the contract. Important if there's a dispute — you may need to travel for legal proceedings.",
            "Non-Disparagement": "This prevents you from making negative public statements about the other party, even if true. Can limit honest reviews and free speech.",
            "Covenant Not To Sue": "This is a waiver of your right to take legal action. You're giving up your ability to sue, which is a significant rights surrender.",
            "Audit Rights": "This gives one party the right to inspect the other's records. Can be intrusive but is common in business agreements.",
            "Insurance": "This requires one or both parties to maintain insurance coverage. Check the type, amount, and who is named as a beneficiary.",
            "Minimum Commitment": "This requires a minimum purchase, spend, or activity level. You're obligated to meet this minimum regardless of your actual needs.",
            "Anti-Assignment": "This prevents transferring your rights or obligations under this contract to someone else without consent.",
            "Warranty Duration": "This specifies how long the warranty or guarantee lasts. After this period, you may have no recourse for defects.",
            "Post-Termination Services": "These are obligations that continue even after the contract ends. Check what you're still required to do.",
        }
        return descriptions.get(clause_type, "")
    
    def _extract_specific_concerns(self, clause_text: str, clause_type: str) -> List[str]:
        """Extract specific concerns from the clause text."""
        concerns = []
        text_lower = clause_text.lower()
        
        # Duration concerns
        duration_match = re.search(
            r'(?:period of|for)\s+(\w+)\s*\(?(\d+)\)?\s*(years?|months?|days?)',
            text_lower
        )
        if duration_match:
            period = f"{duration_match.group(2)} {duration_match.group(3)}"
            if clause_type in ["Non-Compete", "Confidentiality", "Non-Disparagement"]:
                concerns.append(f"Duration: {period} — check if this is reasonable for your situation")
        
        # "Sole discretion" detection
        if "sole discretion" in text_lower:
            concerns.append("Contains 'sole discretion' — one party has unchecked decision-making power")
        
        # "Perpetuity" / "indefinitely" detection
        if any(word in text_lower for word in ["perpetuity", "perpetual", "indefinitely", "indefinite"]):
            concerns.append("This obligation lasts FOREVER — there is no end date")
        
        # "Irrevocable" detection
        if "irrevocable" in text_lower or "irrevocably" in text_lower:
            concerns.append("This is IRREVOCABLE — once agreed, it cannot be undone")
        
        # One-sided termination
        if "at any time" in text_lower and ("without cause" in text_lower or "without reason" in text_lower or "for any reason" in text_lower):
            concerns.append("Allows termination at any time without cause — check if this is mutual")
        
        # Financial penalties
        fee_match = re.search(r'\$[\d,]+(?:\.\d{2})?', clause_text)
        if fee_match:
            concerns.append(f"Contains a specific financial penalty: {fee_match.group(0)}")
        
        # Geographic scope
        geo_match = re.search(r'(\d+)[\s-]*mile radius', text_lower)
        if geo_match:
            concerns.append(f"Geographic restriction: {geo_match.group(1)}-mile radius")
        
        # Waiver of rights
        if re.search(r'waive.*(?:right|claim|action)', text_lower):
            concerns.append("Contains a waiver of legal rights — you're giving up protections")
        
        return concerns[:5]  # Limit to 5 most important
    
    def _generate_summary(self, clause_type: str, role: str, risk_level: str) -> str:
        """Generate a one-line summary."""
        risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        emoji = risk_emoji.get(risk_level, "⚪")
        
        role_data = self.role_templates.get(role, {})
        perspective = role_data.get("perspective", "In general")
        
        return f"{emoji} {perspective}, this {clause_type.lower()} clause is {risk_level.lower()} risk."


# Module-level instance
_explainer_instance = None

def get_explainer(data_dir: Optional[str] = None) -> Explainer:
    """Get or create the explainer singleton."""
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = Explainer(data_dir)
    return _explainer_instance
