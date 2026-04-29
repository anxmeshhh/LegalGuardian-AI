"""
LegalGuardian AI — Recommendation Engine

Generates actionable, role-specific recommendations based on
detected clause types and risk levels.
"""

from typing import Dict, List, Optional


# ─── Recommendation Database ─────────────────────────────────────────────────
# Organized by clause_type → risk_level → role → recommendations

RECOMMENDATIONS = {
    "Indemnification": {
        "HIGH": {
            "default": [
                "💡 Negotiate for MUTUAL indemnification — both parties should share liability",
                "💡 Add a cap on indemnification amount (e.g., total contract value)",
                "💡 Exclude indirect/consequential damages from indemnification scope",
                "⚖️ Consider adding a 'sole negligence' carve-out — you shouldn't indemnify them for their own mistakes"
            ],
            "employee": [
                "💡 Push back on one-sided indemnification — as an employee, your exposure should be limited",
                "💡 Ensure the company's D&O insurance covers your actions taken within scope of employment",
                "⚖️ Ask for removal or cap — individual employees rarely have the financial capacity for unlimited indemnification"
            ],
            "service_provider": [
                "💡 Cap indemnification at the total fees paid under the contract",
                "💡 Limit indemnification to cases of gross negligence or willful misconduct",
                "💡 Require the client to give prompt notice of any claims for indemnification to apply"
            ],
            "tenant": [
                "💡 Negotiate for mutual indemnification — landlord should also be responsible for their negligence",
                "💡 Remove 'regardless of cause' language — you shouldn't cover the landlord's negligence",
                "💡 Ensure renter's insurance is sufficient to cover indemnification obligations"
            ]
        },
        "MEDIUM": {
            "default": [
                "💡 Review the scope of indemnification carefully",
                "💡 Ensure indemnification is mutual where possible"
            ]
        }
    },
    "Uncapped Liability": {
        "HIGH": {
            "default": [
                "🔴 CRITICAL: Negotiate a liability cap — unlimited liability is the #1 risk in any contract",
                "💡 Common cap: 1x to 3x the total contract value",
                "💡 At minimum, exclude indirect/consequential damages",
                "💡 Consider adding professional liability insurance as a safety net"
            ],
            "service_provider": [
                "🔴 NEVER accept unlimited liability as a freelancer/service provider",
                "💡 Standard cap: Total fees paid or to be paid under the contract",
                "💡 Insist on excluding lost profits, consequential, and punitive damages",
                "💡 Get professional liability (E&O) insurance to protect yourself"
            ],
            "employee": [
                "🔴 Individual employees should NEVER have unlimited personal liability",
                "💡 Request removal of this clause or a cap at your annual salary",
                "💡 Ensure company insurance covers your work-related actions"
            ]
        }
    },
    "Non-Compete": {
        "HIGH": {
            "default": [
                "💡 Negotiate a shorter duration (6 months is more reasonable than 2 years)",
                "💡 Narrow the geographic scope to specific cities/regions, not entire states",
                "💡 Define 'competitor' precisely — vague definitions can block you from entire industries",
                "⚖️ Note: Many jurisdictions limit or ban non-competes — check your local laws"
            ],
            "employee": [
                "💡 Push for maximum 6-12 months — courts often strike down longer periods",
                "💡 Request 'garden leave' pay — if they want to restrict your work, they should pay you during that period",
                "💡 Narrow the scope: it should only cover your specific role, not the entire industry",
                "⚖️ California, Colorado, Minnesota, North Dakota, and Oklahoma have banned most non-competes — check if yours is enforceable"
            ],
            "service_provider": [
                "💡 Reject or limit to 3-6 months — as a freelancer, this directly cuts your income",
                "💡 Ensure the non-compete only covers the specific project area, not all your skills",
                "💡 Request additional compensation for the non-compete period"
            ]
        }
    },
    "Termination For Convenience": {
        "HIGH": {
            "default": [
                "💡 Ensure termination rights are MUTUAL — both parties should have the same right",
                "💡 Negotiate a longer notice period (30-60 days minimum)",
                "💡 Add a 'wind-down' clause for payment of work in progress"
            ],
            "service_provider": [
                "💡 Add a 'kill fee' clause — if they terminate early, you should be compensated",
                "💡 Require payment for all completed work, not just 'accepted' work",
                "💡 Negotiate minimum project commitment before termination rights kick in"
            ],
            "employee": [
                "💡 Negotiate a severance package if terminated without cause",
                "💡 Ensure adequate notice period (30-60 days)",
                "💡 Clarify what happens to vested benefits upon termination"
            ],
            "tenant": [
                "💡 Ensure YOU also have the right to terminate early (mutual right)",
                "💡 Check if the notice period is the same for both parties",
                "💡 Negotiate the early termination fee to a reasonable amount"
            ]
        }
    },
    "Ip Ownership Assignment": {
        "HIGH": {
            "default": [
                "💡 Negotiate to retain rights to pre-existing IP and general skills/knowledge",
                "💡 Request a license-back for portfolio/showcase purposes",
                "💡 Limit assignment to work specifically created for this contract"
            ],
            "service_provider": [
                "🔴 This transfers ALL your creative work to the client — be very careful",
                "💡 Retain the right to display the work in your portfolio",
                "💡 Exclude pre-existing code, libraries, and tools you brought to the project",
                "💡 Negotiate: assignment happens only AFTER full payment is received",
                "💡 Keep rights to general methodologies and non-client-specific code"
            ],
            "employee": [
                "💡 Ensure the assignment is limited to work done within scope of employment",
                "💡 Clarify that personal projects and side work are excluded",
                "💡 Check if 'during working hours' vs 'at any time' — the latter is very broad"
            ]
        }
    },
    "Renewal Term": {
        "MEDIUM": {
            "default": [
                "📅 Set a calendar reminder for the cancellation deadline",
                "💡 Negotiate a shorter auto-renewal period (month-to-month instead of annual)",
                "💡 Request email notification before auto-renewal kicks in"
            ],
            "tenant": [
                "📅 CRITICAL: Set a calendar reminder {notice_period} before lease end",
                "💡 Negotiate mutual notice periods — both parties should give the same notice",
                "💡 Ask for a rent cap on renewals (e.g., max 3-5% increase)"
            ]
        },
        "HIGH": {
            "tenant": [
                "🔴 The notice periods are heavily one-sided — you need 90 days but they only need 30",
                "💡 Negotiate equal notice periods for both parties",
                "📅 Set multiple calendar reminders — missing the window could cost thousands"
            ]
        }
    },
    "Liquidated Damages": {
        "HIGH": {
            "default": [
                "💡 Verify the penalty amount is reasonable and proportional to actual damages",
                "💡 Courts may not enforce penalties deemed excessive — but fighting it costs money",
                "💡 Negotiate a lower amount or a sliding scale based on timing"
            ]
        }
    },
    "Covenant Not To Sue": {
        "HIGH": {
            "default": [
                "🔴 You are giving up your right to take legal action — this is a MAJOR concession",
                "💡 Request removal of this clause — it's heavily one-sided",
                "💡 If it must stay, ensure it's mutual and limited in scope",
                "⚖️ Consider what protections you're losing and whether arbitration is an adequate substitute"
            ]
        }
    },
    "Confidentiality": {
        "MEDIUM": {
            "default": [
                "💡 Check the duration — 2-3 years is standard; 'in perpetuity' is aggressive",
                "💡 Ensure there are carve-outs for publicly available information",
                "💡 Verify that standard business information isn't over-classified as confidential"
            ]
        }
    },
    "Exclusivity": {
        "HIGH": {
            "default": [
                "💡 Negotiate a narrower scope — define 'competing' precisely",
                "💡 Add a sunset clause — exclusivity should have an end date",
                "💡 Request additional compensation for exclusivity"
            ],
            "service_provider": [
                "🔴 Exclusivity means you CANNOT work with anyone else in this space",
                "💡 Reject unless the client is paying a premium for exclusivity",
                "💡 Limit exclusivity to the specific project, not your entire business",
                "💡 Add a minimum revenue guarantee if exclusivity is required"
            ]
        }
    }
}

# Generic recommendations for clause types not covered above
GENERIC_RECOMMENDATIONS = {
    "HIGH": [
        "⚠️ This is a high-risk clause — consult a legal professional before signing",
        "💡 Negotiate to reduce the severity or add protective conditions",
        "💡 Consider whether this clause is standard in your industry"
    ],
    "MEDIUM": [
        "💡 Review this clause carefully and consider negotiating terms",
        "💡 Ensure the terms are mutual and balanced between both parties"
    ],
    "LOW": [
        "✅ This appears to be a standard clause with minimal risk",
        "💡 Still worth reading to ensure it matches your expectations"
    ]
}


class Recommender:
    """Generates actionable, role-specific recommendations."""
    
    def get_recommendations(self, clause_type: str, risk_level: str,
                           role: str) -> List[str]:
        """
        Get recommendations for a specific clause.
        
        Args:
            clause_type: The classified clause type
            risk_level: Risk level (HIGH/MEDIUM/LOW)
            role: User's role
        
        Returns:
            List of recommendation strings
        """
        recs = []
        
        # Check specific recommendations
        clause_recs = RECOMMENDATIONS.get(clause_type, {})
        level_recs = clause_recs.get(risk_level, {})
        
        # Try role-specific first, then default
        if role in level_recs:
            recs = level_recs[role]
        elif "default" in level_recs:
            recs = level_recs["default"]
        
        # If no specific recommendations, use generic
        if not recs:
            recs = GENERIC_RECOMMENDATIONS.get(risk_level, [])
        
        # Always add the disclaimer for high-risk clauses
        if risk_level == "HIGH" and not any("consult" in r.lower() for r in recs):
            recs.append("⚖️ Consider consulting a legal professional before signing")
        
        return recs
    
    def get_document_recommendations(self, clause_analyses: List[Dict]) -> List[str]:
        """
        Generate overall document-level recommendations.
        
        Args:
            clause_analyses: List of analyzed clauses with types and risk levels
        
        Returns:
            List of document-level recommendation strings
        """
        recs = []
        high_risk_count = sum(1 for c in clause_analyses if c.get("risk_level") == "HIGH")
        medium_risk_count = sum(1 for c in clause_analyses if c.get("risk_level") == "MEDIUM")
        
        if high_risk_count >= 3:
            recs.append("🔴 This contract has MULTIPLE high-risk clauses. Strongly recommend professional legal review before signing.")
        elif high_risk_count >= 1:
            recs.append(f"⚠️ This contract has {high_risk_count} high-risk clause(s). Review them carefully before signing.")
        
        if medium_risk_count >= 5:
            recs.append("🟡 Several medium-risk clauses detected. While individually manageable, the cumulative effect increases your overall exposure.")
        
        # Check for specific dangerous combinations
        clause_types = [c.get("clause_type", "") for c in clause_analyses]
        
        if "Uncapped Liability" in clause_types and "Indemnification" in clause_types:
            recs.append("🔴 DANGEROUS COMBINATION: Uncapped liability + indemnification = potentially infinite financial exposure. Negotiate caps immediately.")
        
        if "Non-Compete" in clause_types and "Exclusivity" in clause_types:
            recs.append("⚠️ Both non-compete AND exclusivity clauses present — this severely limits your business freedom during AND after this contract.")
        
        if "Termination For Convenience" in clause_types and "Ip Ownership Assignment" in clause_types:
            recs.append("⚠️ The other party can terminate at will AND owns all your work. Risk: you do significant work, they terminate, and keep everything.")
        
        # Always add this
        recs.append("📋 Remember: This analysis is informational only and does not constitute legal advice.")
        
        return recs


# Module-level instance
_recommender_instance = None

def get_recommender() -> Recommender:
    """Get or create the recommender singleton."""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = Recommender()
    return _recommender_instance
