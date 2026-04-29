"""Quick test of the LegalGuardian AI API pipeline."""
import sys, os
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
import json

BASE = "http://localhost:5000"

# Test 1: Health check
r = requests.get(f"{BASE}/api/health")
print(f"[1] Health: {r.status_code} => {r.json()}")

# Test 2: Doc types
r = requests.get(f"{BASE}/api/doc-types")
types = r.json()["document_types"]
print(f"[2] Doc types: {len(types)} types loaded")

# Test 3: Analyze contract
contract = """Section 1. Non-Compete Covenant
For a period of two (2) years following termination of this Agreement, the Employee shall not, directly or indirectly, engage in any business that competes with the Employer within a 100-mile radius of any Employer office.

Section 2. Indemnification
The Employee shall indemnify, defend, and hold harmless the Employer from any and all claims, damages, losses, and expenses. The Employee waives all rights to sue the Employer.

Section 3. Intellectual Property Assignment
All work product, inventions, and code created by the Employee shall be the sole and exclusive property of the Employer. The Employee irrevocably assigns all intellectual property rights to the Employer.

Section 4. Termination for Convenience
The Employer may terminate this Agreement at any time, for any reason or no reason, with seven (7) days notice. The Employee may only terminate with sixty (60) days written notice.

Section 5. Confidentiality
The Employee agrees to maintain strict confidentiality regarding all proprietary information and trade secrets, in perpetuity.
"""

r = requests.post(f"{BASE}/api/analyze", json={
    "contract_text": contract,
    "document_type": "employment_contract",
    "user_role": "employee"
})
data = r.json()

print(f"\n[3] Analysis: {r.status_code}")
print(f"    Overall Risk: {data['document_summary']['overall_risk_level']} (score: {data['document_summary']['overall_risk_score']})")
print(f"    Total Clauses: {data['document_summary']['total_clauses']}")
print(f"    Breakdown: {json.dumps(data['document_summary']['risk_breakdown'])}")
print(f"    Doc Recs: {len(data['document_summary']['document_recommendations'])} recommendations")
print()

for c in data["clauses"]:
    print(f"    #{c['id']} [{c['risk_level']:>6} {c['risk_score']:>3}/100] {c['clause_type']}")
    print(f"       One-sided: {c['is_one_sided']} | Method: {c['classification_method']} | Conf: {c['classification_confidence']}")
    if c['attention_words']:
        print(f"       Attention: {', '.join(c['attention_words'][:3])}")
    if c['recommendations']:
        print(f"       Recs: {c['recommendations'][0][:80]}...")
    print()

# Test 4: Q&A
r = requests.post(f"{BASE}/api/qa", json={
    "contract_text": contract,
    "question": "What happens if I terminate early?"
})
qa = r.json()
print(f"[4] Q&A: {r.status_code}")
print(f"    Answer: {qa['answer'][:150]}...")
print(f"    Confidence: {qa['confidence']} | Method: {qa['method']}")

print("\n=== ALL TESTS PASSED ===")
