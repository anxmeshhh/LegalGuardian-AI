"""
LegalGuardian AI — Application Entry Point

Usage:
    python run.py

The application will start at http://localhost:5000
"""

from backend.app import app

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  ⚖️  LegalGuardian AI")
    print("  NLP-Powered Contract Risk Analysis")
    print("="*50)
    print(f"\n  🌐 Open in browser: http://localhost:5000")
    print(f"  📡 API docs:        http://localhost:5000/api/health")
    print(f"\n  Press Ctrl+C to stop\n")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
