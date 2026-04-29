# ⚖️ LegalGuardian AI

> **NLP-Powered Legal Contract Risk Analysis & Decision-Support System**

LegalGuardian AI analyzes your legal contracts clause-by-clause, identifies risks personalized to **your role** (e.g., tenant vs. landlord), and explains everything in plain English — no lawyer needed.

---

## 🎯 What Problem Does This Solve?

**99% of people don't read what they sign.** Not because they're careless — because legal documents are *designed* to be unreadable.

| The Problem | LegalGuardian AI Solution |
|---|---|
| Contracts are full of unreadable legalese | **Plain-English translations** of every risky clause |
| Hidden clauses trap users (auto-renewal, non-competes) | **Automatic detection** of 41 clause types with risk scoring |
| Legal review costs $300–$1,000+ per hour | **Instant, free analysis** powered by NLP |
| Generic analysis doesn't consider YOUR position | **Role-aware personalization** — same clause, different risk for each party |
| No way to ask "What does Section 5 mean for me?" | **Interactive Q&A** — ask questions, get answers from the contract |

---

## 🧠 How It Works

LegalGuardian AI uses a **3-step input process** and a **multi-stage NLP pipeline**:

```
📄 YOUR INPUT                    🔧 NLP PIPELINE                   📊 OUTPUT
─────────────                    ──────────────                    ──────────
                                 
Step 1: Document Type    ───►    Text Extraction           ───►   Risk Dashboard
   (Employment, Rental...)       (PDF / DOCX / Text)              (Overall Score)
                                       │                                │
Step 2: Your Role        ───►    Clause Segmentation       ───►   Clause-by-Clause
   (Employee, Tenant...)         (Section detection)              Risk Cards
                                       │                                │
Step 3: Contract Text    ───►    Clause Classification     ───►   Heatmap
   (Paste or Upload)             (41 CUAD categories)             Visualization
                                       │                                │
                                 Role-Aware Risk Scoring   ───►   Explanations &
                                 (Personalized to YOU)            Recommendations
                                       │                                │
                                 Plain-English Explainer   ───►   Interactive Q&A
                                 + Legal Dictionary               Chat Panel
```

### The Smart 3-Step Input

With just **two clicks + one paste**, the analysis becomes personalized:

| Without Role Context | With Role Context |
|---|---|
| "This clause limits liability" | "⚠️ This clause means **YOU** bear all liability as the tenant" |
| "Non-compete for 2 years" | "🔴 As the employee, you **cannot work in this industry for 2 years**" |
| "Auto-renewal with 90-day notice" | "🔴 **You** must give 90 days notice, but **they** can terminate in 7 days" |

---

## 🏗️ System Architecture

```
LegalGuardian-AI/
│
├── backend/                          # FastAPI Python Backend
│   ├── app.py                        # API server (main entry point)
│   ├── config.py                     # Configuration & constants
│   │
│   ├── models/                       # ML / Classification Models
│   │   ├── clause_classifier.py      # Keyword + Transformer clause classification
│   │   ├── risk_scorer.py            # Role-aware risk scoring engine
│   │   └── qa_model.py               # Interactive Q&A (BERT-based)
│   │
│   ├── services/                     # Business Logic Services
│   │   ├── preprocessor.py           # Text extraction & clause segmentation
│   │   ├── explainer.py              # Plain-English explanation generator
│   │   └── recommender.py            # Actionable recommendation engine
│   │
│   ├── data/                         # Static Data Files
│   │   ├── risk_mappings.json        # 41 CUAD clause types → risk levels
│   │   ├── legal_dictionary.json     # 30+ legal terms → plain English
│   │   └── role_templates.json       # Role-specific explanation templates
│   │
│   └── checkpoints/                  # Model weights (gitignored)
│
├── frontend/                         # Web Interface (HTML/CSS/JS)
│   ├── index.html                    # Main SPA page
│   │
│   ├── css/                          # Modular Stylesheets
│   │   ├── variables.css             # Design tokens & CSS custom properties
│   │   ├── base.css                  # Layout, navigation, hero, footer
│   │   ├── components.css            # Buttons, inputs, selects
│   │   ├── input-panel.css           # 3-step input form
│   │   ├── results.css               # Risk dashboard, heatmap, clause cards
│   │   ├── qa-panel.css              # Q&A chat interface
│   │   ├── animations.css            # Micro-animations & transitions
│   │   └── responsive.css            # Mobile & tablet breakpoints
│   │
│   └── js/                           # Modular JavaScript
│       ├── config.js                 # API endpoints & sample contracts
│       ├── api.js                    # Backend communication layer
│       ├── ui.js                     # DOM utilities & form management
│       ├── results.js                # Results rendering (gauge, cards, heatmap)
│       ├── qa.js                     # Q&A chat panel controller
│       └── app.js                    # Main application controller
│
├── sample_contracts/                 # Demo Contracts for Testing
│   ├── employment_contract.txt       # Employment agreement (risky clauses)
│   ├── rental_agreement.txt          # Rental lease (tenant-unfavorable)
│   └── freelance_agreement.txt       # Freelance contract (provider-unfavorable)
│
├── requirements.txt                  # Python dependencies
├── LICENSE                           # MIT License
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/anxmeshhh/LegalGuardian-AI.git
cd LegalGuardian-AI
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python -m uvicorn backend.app:app --reload --port 8000
```

### 4. Open in Browser

Navigate to **http://localhost:8000** — the app will load with the premium dark-themed UI.

### 5. Try It Out

1. **Select** a document type (e.g., "Employment Contract")
2. **Select** your role (e.g., "I am the Employee")
3. **Paste** your contract text (or click a sample button)
4. **Click** "Analyze Contract"
5. **Review** the risk dashboard, clause cards, and recommendations
6. **Ask** questions in the Q&A panel

---

## 📊 NLP Pipeline Details

### Clause Classification (41 CUAD Categories)

The system identifies clause types using a **dual-mode classifier**:

| Mode | How It Works | When Used |
|---|---|---|
| **Keyword-based** | Regex pattern matching against 41 clause type signatures | Default (works immediately, no model download) |
| **Transformer-based** | Fine-tuned Legal-BERT on CUAD dataset | When model checkpoint is available in `backend/checkpoints/` |

**Supported Clause Types** include: Indemnification, Non-Compete, Termination, IP Assignment, Liability Limitation, Confidentiality, Auto-Renewal, Governing Law, and 33 more.

### Role-Aware Risk Scoring

The same clause gets **different risk scores** depending on your role:

```
Example: "Termination for Convenience" clause

  As Employee:   🔴 HIGH RISK (score: 85)
                 "The employer can terminate at any time without cause"

  As Employer:   🟢 LOW RISK (score: 20)
                 "You retain flexibility to end employment"
```

Risk is computed from three factors:
1. **Base risk** — inherent clause type risk (from CUAD mapping)
2. **Role modifier** — how the clause affects YOUR position
3. **Text analysis** — dangerous keywords like "unlimited", "irrevocable", "sole discretion"

### Plain-English Explanations

Every clause gets:
- ⚠️ **Risk-level indicator** (HIGH / MEDIUM / LOW)
- 📖 **What it means** in simple language
- 👤 **Impact on YOU** based on your role
- ⚠️ **Specific concerns** extracted from the text (duration, financial penalties, one-sidedness)
- 💡 **Actionable recommendations** for negotiation

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | GET | Serve the web frontend |
| `GET /api/health` | GET | Health check |
| `GET /api/doc-types` | GET | List document types and role options |
| `POST /api/analyze` | POST | Analyze contract text (JSON body) |
| `POST /api/analyze-file` | POST | Analyze uploaded file (multipart form) |
| `POST /api/qa` | POST | Ask a question about the contract |

### `POST /api/analyze` — Request

```json
{
  "contract_text": "This Agreement is entered into...",
  "document_type": "employment_contract",
  "user_role": "employee"
}
```

### Response

```json
{
  "document_summary": {
    "total_clauses": 12,
    "risk_breakdown": { "high": 3, "medium": 4, "low": 5 },
    "overall_risk_score": 72,
    "overall_risk_level": "HIGH"
  },
  "clauses": [
    {
      "id": 1,
      "title": "Non-Compete Covenant",
      "clause_type": "Non-Compete",
      "risk_level": "HIGH",
      "risk_score": 88,
      "explanation": "⚠️ HIGH RISK — As the employee, you cannot work in this industry...",
      "recommendations": ["💡 Negotiate a shorter duration (6 months)..."],
      "key_terms": [{ "term": "non-compete", "plain_english": "..." }],
      "attention_words": ["non-compete", "2 years", "100-mile radius"]
    }
  ],
  "disclaimer": "This analysis is for informational purposes only..."
}
```

---

## 📁 Supported Document Types

| Document Type | Role A | Role B |
|---|---|---|
| Employment Contract | Employee | Employer |
| Rental/Lease Agreement | Tenant | Landlord |
| Freelance/Service Agreement | Service Provider | Client |
| Loan/EMI Agreement | Borrower | Lender |
| NDA | Disclosing Party | Receiving Party |
| Insurance Policy | Policyholder | Insurer |
| Terms of Service | User | Platform |
| Partnership Agreement | Partner A | Partner B |
| Other | General Analysis | — |

---

## 🧪 Sample Contracts

Three realistic sample contracts are included for testing, each designed with intentionally risky clauses:

| Contract | Key Risks to Find |
|---|---|
| **Employment** | 2-year non-compete, unlimited IP assignment, one-sided indemnification |
| **Rental** | 90/30-day asymmetric renewal notice, tenant bears all repairs, landlord negligence waiver |
| **Freelance** | Unlimited liability for provider, full IP transfer with no portfolio rights, one-sided termination |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI (Python) | REST API, async, auto-docs at `/docs` |
| **ML/NLP** | PyTorch + Transformers | Legal-BERT, BERT-QA models |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | Premium SPA, no framework needed |
| **Data** | CUAD Dataset | 41 clause types, 510 contracts |
| **Fonts** | Inter + JetBrains Mono | Modern typography |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ⚠️ Disclaimer

**LegalGuardian AI provides informational analysis only and does not constitute legal advice.** This tool is designed to help users understand their contracts better, but it is not a substitute for professional legal counsel. Always consult a qualified attorney for legal matters, especially for high-risk findings.
