"""
LegalGuardian AI — Clause Classification Model

Supports two modes:
1. Fine-tuned Legal-BERT (when checkpoint is available)
2. Zero-shot classification fallback (works out of the box)

Uses keyword-based classification as the primary strategy for the prototype,
with transformer-based classification available when models are loaded.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Keyword-based clause classification patterns
# Maps clause types to distinctive keywords/phrases
CLAUSE_KEYWORDS = {
    "Indemnification": [
        "indemnif", "hold harmless", "defend and hold", "indemnity",
        "compensate for loss", "make whole"
    ],
    "Uncapped Liability": [
        "unlimited liability", "no limit on liability", "liability shall be unlimited",
        "without limitation", "unlimited damages"
    ],
    "Cap On Liability": [
        "liability shall not exceed", "cap on liability", "maximum liability",
        "aggregate liability", "total liability shall be limited",
        "liability cap", "not exceed the"
    ],
    "Limitation of Liability": [
        "limitation of liability", "limit of liability", "no liability for",
        "shall not be liable", "disclaims all liability", "in no event shall",
        "consequential damages", "indirect damages", "punitive damages",
        "special damages", "incidental damages"
    ],
    "Non-Compete": [
        "non-compete", "noncompete", "not compete", "shall not.*engage in.*business",
        "shall not.*provide.*similar services.*competitor",
        "competitive activity", "competing business"
    ],
    "Exclusivity": [
        "exclusiv", "sole and exclusive", "exclusive right",
        "only provider", "exclusive basis"
    ],
    "Termination For Convenience": [
        "terminate.*at any time", "terminate.*for any reason",
        "terminate.*without cause", "terminate.*for convenience",
        "termination without cause", "terminate.*no reason"
    ],
    "Non-Disparagement": [
        "non-disparagement", "nondisparagement", "not.*disparage",
        "not.*defame", "negative.*statement", "not make.*public statement"
    ],
    "Ip Ownership Assignment": [
        "intellectual property.*assign", "ip.*assign", "hereby assign",
        "work.*shall be.*property", "sole and exclusive property",
        "assigns all right.*title", "work product.*belong",
        "work for hire", "all inventions.*shall be"
    ],
    "Confidentiality": [
        "confidential", "non-disclosure", "nondisclosure", "trade secret",
        "proprietary information", "not disclose", "maintain.*secrecy"
    ],
    "Non-Transferable License": [
        "non-transferable", "nontransferable", "may not transfer",
        "may not assign.*license"
    ],
    "License Grant": [
        "grants.*license", "license to use", "hereby grants",
        "right to use", "licensed under"
    ],
    "Governing Law": [
        "governing law", "governed by.*laws", "construed in accordance",
        "jurisdiction", "applicable law", "laws of the state"
    ],
    "Termination": [
        "terminat", "termination", "term and termination",
        "early termination", "right to terminate"
    ],
    "Renewal Term": [
        "auto.*renew", "automatic.*renew", "automatically renew",
        "successive.*term", "renewal term", "auto-renewal"
    ],
    "Notice Period To Terminate Renewal": [
        "notice.*non-renewal", "notice.*terminate.*renewal",
        "days.*written notice.*renew", "notice period.*renewal"
    ],
    "No-Solicit Of Employees": [
        "not.*solicit.*employee", "non-solicitation.*employee",
        "not.*recruit.*hire.*employee"
    ],
    "No-Solicit Of Customers": [
        "not.*solicit.*client", "not.*solicit.*customer",
        "non-solicitation.*customer", "non-solicitation.*client"
    ],
    "Liquidated Damages": [
        "liquidated damage", "pre-determined.*damage", "stipulated damage",
        "penalty.*breach", "termination fee", "early termination.*fee"
    ],
    "Warranty Duration": [
        "warranty.*period", "warranty.*month", "warranty.*year",
        "warrant.*free from.*defect", "warranty duration"
    ],
    "Audit Rights": [
        "audit right", "right to audit", "right to inspect",
        "right to examine.*record", "access to.*books.*records"
    ],
    "Insurance": [
        "insurance", "maintain.*coverage", "insurance policy",
        "additional insured", "certificate of insurance"
    ],
    "Covenant Not To Sue": [
        "covenant not to sue", "waive.*right to sue", "not.*bring.*action",
        "release.*claims", "waives.*right.*jury trial"
    ],
    "Anti-Assignment": [
        "may not assign", "shall not assign", "anti-assignment",
        "not.*transfer.*right.*without.*consent"
    ],
    "Minimum Commitment": [
        "minimum.*commitment", "minimum.*purchase", "minimum.*order",
        "minimum.*volume", "guaranteed minimum"
    ],
    "Revenue/Profit Sharing": [
        "revenue.*shar", "profit.*shar", "royalt",
        "percentage.*revenue", "percentage.*profit"
    ],
    "Price Restrictions": [
        "price.*restriction", "pricing.*limitation", "price.*cap",
        "shall not.*increase.*price.*more than"
    ],
    "Most Favored Nation": [
        "most favored", "most-favored", "best price",
        "no less favorable"
    ],
    "Change Of Control": [
        "change of control", "change in control", "merger.*acquisition",
        "acquir.*all.*assets"
    ],
    "Irrevocable Or Perpetual License": [
        "irrevocable.*license", "perpetual.*license",
        "irrevocable and perpetual"
    ],
    "Post-Termination Services": [
        "post-termination", "after termination.*shall",
        "survive.*termination", "obligation.*survive"
    ],
    "Third Party Beneficiary": [
        "third party beneficiar", "third-party beneficiar",
        "intended beneficiar"
    ],
    "Source Code Escrow": [
        "source code escrow", "escrow.*source code",
        "code.*escrow agent"
    ],
    "Rofr/Rofo/Rofn": [
        "right of first refusal", "right of first offer",
        "first right.*negotiat", "ROFR", "ROFO"
    ],
    "Volume Restriction": [
        "volume.*restrict", "volume.*limit", "production.*cap",
        "maximum.*volume"
    ],
    "Joint Ip Ownership": [
        "joint.*ownership.*ip", "jointly.*own", "co-own",
        "shared.*intellectual property"
    ],
    "Affiliate License-Licensor": [
        "licensor.*affiliate.*license", "affiliate.*licensor"
    ],
    "Affiliate License-Licensee": [
        "licensee.*affiliate.*license", "affiliate.*licensee"
    ],
    "Unlimited/All-You-Can-Eat License": [
        "unlimited.*license", "all-you-can-eat", "unlimited use"
    ],
    "Document Name": [
        "this agreement", "this contract", "this lease",
        "this license", "this policy"
    ],
    "Parties": [
        "entered into by and between", "by and between",
        "hereinafter referred to as", "the parties"
    ],
    "Agreement Date": [
        "dated as of", "effective as of", "entered into as of",
        "this.*day of"
    ],
    "Effective Date": [
        "effective date", "commencement date", "start date"
    ],
    "Expiration Date": [
        "expiration date", "end date", "terminates on",
        "shall expire"
    ]
}


class ClauseClassifier:
    """
    Classifies legal clauses into CUAD categories and predicts risk levels.
    
    Primary: Keyword-based classification (works immediately, no model needed)
    Secondary: Transformer-based classification (when model checkpoint is available)
    """
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.checkpoint_path = checkpoint_path
        self.transformer_model = None
        self.tokenizer = None
        self._model_loaded = False
        
        # Try to load transformer model if checkpoint exists
        if checkpoint_path and Path(checkpoint_path).exists():
            self._load_transformer_model(checkpoint_path)
    
    def _load_transformer_model(self, checkpoint_path: str):
        """Load fine-tuned Legal-BERT model."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
            self.transformer_model = AutoModelForSequenceClassification.from_pretrained(
                checkpoint_path
            )
            self.transformer_model.eval()
            self._model_loaded = True
            print(f"✅ Loaded fine-tuned model from {checkpoint_path}")
        except Exception as e:
            print(f"⚠️ Could not load transformer model: {e}")
            print("   Falling back to keyword-based classification")
            self._model_loaded = False
    
    def classify(self, clause_text: str) -> Dict:
        """
        Classify a clause into a CUAD category.
        
        Returns:
            Dict with 'clause_type', 'confidence', 'method', and 'matched_keywords'
        """
        if self._model_loaded:
            return self._classify_transformer(clause_text)
        return self._classify_keywords(clause_text)
    
    def _classify_keywords(self, clause_text: str) -> Dict:
        """Keyword-based clause classification."""
        text_lower = clause_text.lower()
        scores = {}
        matched = {}
        
        for clause_type, keywords in CLAUSE_KEYWORDS.items():
            score = 0
            found_keywords = []
            for keyword in keywords:
                # Use regex for patterns with wildcards, simple 'in' for others
                if '.*' in keyword or '(' in keyword:
                    if re.search(keyword, text_lower, re.IGNORECASE):
                        score += 2
                        found_keywords.append(keyword)
                else:
                    if keyword.lower() in text_lower:
                        score += 2
                        found_keywords.append(keyword)
            
            if score > 0:
                scores[clause_type] = score
                matched[clause_type] = found_keywords
        
        if not scores:
            return {
                "clause_type": "General Clause",
                "confidence": 0.3,
                "method": "keyword",
                "matched_keywords": [],
                "all_matches": []
            }
        
        # Get the best match
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        
        # Normalize confidence (more keywords matched = higher confidence)
        total_keywords = len(CLAUSE_KEYWORDS.get(best_type, []))
        confidence = min(0.95, 0.4 + (max_score / max(total_keywords * 2, 1)) * 0.55)
        
        # Also return secondary matches for multi-label awareness
        sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        all_matches = [
            {"clause_type": ct, "score": s, "keywords": matched.get(ct, [])}
            for ct, s in sorted_matches[:5]
        ]
        
        return {
            "clause_type": best_type,
            "confidence": round(confidence, 3),
            "method": "keyword",
            "matched_keywords": matched.get(best_type, []),
            "all_matches": all_matches
        }
    
    def _classify_transformer(self, clause_text: str) -> Dict:
        """Transformer-based clause classification (when model is available)."""
        try:
            import torch
            
            inputs = self.tokenizer(
                clause_text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                confidence, predicted = torch.max(probs, dim=-1)
            
            # Map index to clause type (requires label mapping from training)
            from ..config import CUAD_CLAUSE_TYPES
            clause_type = CUAD_CLAUSE_TYPES[predicted.item()] if predicted.item() < len(CUAD_CLAUSE_TYPES) else "General Clause"
            
            return {
                "clause_type": clause_type,
                "confidence": round(confidence.item(), 3),
                "method": "transformer",
                "matched_keywords": [],
                "all_matches": []
            }
        except Exception as e:
            print(f"⚠️ Transformer classification failed: {e}, falling back to keywords")
            return self._classify_keywords(clause_text)
    
    def classify_batch(self, clauses: List[str]) -> List[Dict]:
        """Classify multiple clauses."""
        return [self.classify(clause) for clause in clauses]


# Module-level instance for easy import
_classifier_instance = None

def get_classifier(checkpoint_path: Optional[str] = None) -> ClauseClassifier:
    """Get or create the clause classifier singleton."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ClauseClassifier(checkpoint_path)
    return _classifier_instance
