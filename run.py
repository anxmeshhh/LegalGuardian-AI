"""
LegalGuardian AI -- Application Entry Point

Usage:
    python run.py

The application will start at http://localhost:5000
"""

import sys
import os

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.app import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  LegalGuardian AI")
    print("  NLP-Powered Contract Risk Analysis")
    print("=" * 50)
    print(f"\n  Open in browser: http://localhost:5000")
    print(f"  API health:      http://localhost:5000/api/health")
    print(f"\n  Press Ctrl+C to stop\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
