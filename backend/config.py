"""
LegalGuardian AI — Configuration & Constants
"""

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"

# ─── Model Configuration ─────────────────────────────────────────────────────
MODEL_NAME = "nlpaueb/legal-bert-small-uncased"  # ~55MB, fast inference
QA_MODEL_NAME = "deepset/roberta-base-squad2"    # Pre-trained QA model
MAX_SEQ_LENGTH = 512
DEVICE = "cpu"  # Change to "cuda" if GPU available

# ─── Document Types & Role Mappings ──────────────────────────────────────────
DOCUMENT_TYPES = {
    "employment_contract": {
        "label": "Employment Contract",
        "roles": {
            "employee": "I am the Employee",
            "employer": "I am the Employer"
        }
    },
    "rental_agreement": {
        "label": "Rental/Lease Agreement",
        "roles": {
            "tenant": "I am the Tenant",
            "landlord": "I am the Landlord"
        }
    },
    "freelance_agreement": {
        "label": "Freelance/Service Agreement",
        "roles": {
            "service_provider": "I am the Service Provider",
            "client": "I am the Client"
        }
    },
    "loan_agreement": {
        "label": "Loan/EMI Agreement",
        "roles": {
            "borrower": "I am the Borrower",
            "lender": "I am the Lender"
        }
    },
    "nda": {
        "label": "NDA (Non-Disclosure Agreement)",
        "roles": {
            "disclosing_party": "I am the Disclosing Party",
            "receiving_party": "I am the Receiving Party"
        }
    },
    "insurance_policy": {
        "label": "Insurance Policy",
        "roles": {
            "policyholder": "I am the Policyholder",
            "insurer": "I am the Insurer"
        }
    },
    "terms_of_service": {
        "label": "Terms of Service",
        "roles": {
            "user": "I am the User",
            "platform": "I am the Platform"
        }
    },
    "partnership_agreement": {
        "label": "Partnership Agreement",
        "roles": {
            "partner_a": "I am Partner A",
            "partner_b": "I am Partner B"
        }
    },
    "other": {
        "label": "Other",
        "roles": {
            "general": "General Analysis (no role-based personalization)"
        }
    }
}

# ─── CUAD Clause Types (41 categories) ───────────────────────────────────────
CUAD_CLAUSE_TYPES = [
    "Document Name",
    "Parties",
    "Agreement Date",
    "Effective Date",
    "Expiration Date",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
    "Governing Law",
    "Most Favored Nation",
    "Non-Compete",
    "Exclusivity",
    "No-Solicit Of Customers",
    "No-Solicit Of Employees",
    "Non-Disparagement",
    "Termination For Convenience",
    "Rofr/Rofo/Rofn",
    "Change Of Control",
    "Anti-Assignment",
    "Revenue/Profit Sharing",
    "Price Restrictions",
    "Minimum Commitment",
    "Volume Restriction",
    "Ip Ownership Assignment",
    "Joint Ip Ownership",
    "License Grant",
    "Non-Transferable License",
    "Affiliate License-Licensor",
    "Affiliate License-Licensee",
    "Unlimited/All-You-Can-Eat License",
    "Irrevocable Or Perpetual License",
    "Source Code Escrow",
    "Post-Termination Services",
    "Audit Rights",
    "Uncapped Liability",
    "Cap On Liability",
    "Liquidated Damages",
    "Warranty Duration",
    "Insurance",
    "Covenant Not To Sue",
    "Third Party Beneficiary",
    "Indemnification"
]

# ─── Risk Level Definitions ──────────────────────────────────────────────────
RISK_LEVELS = {
    "HIGH": {"color": "#ef4444", "label": "High Risk", "emoji": "🔴", "score_range": (70, 100)},
    "MEDIUM": {"color": "#f59e0b", "label": "Medium Risk", "emoji": "🟡", "score_range": (40, 69)},
    "LOW": {"color": "#22c55e", "label": "Low Risk", "emoji": "🟢", "score_range": (0, 39)},
}

# ─── Server Configuration ────────────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["*"]  # Allow all origins for development
