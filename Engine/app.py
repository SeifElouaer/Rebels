"""
app.py
------
Flask REST API for CreditTwin credit decision engine
"""

import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from twin_search import find_twins
from vector_store import get_collection_info
from config import COLLECTION_NAME

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)
CORS(app)

# Use absolute path relative to this script to find the DB
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "credit.db")


@app.route("/", methods=["GET"])
def home():
    """Home page with endpoint list"""
    return jsonify({
        "service": "CreditTwin API",
        "version": "1.0.0",
        "description": "Credit decision engine based on financial twin matching",
        "endpoints": {
            "GET /": "API information",
            "POST /api/evaluate": "Evaluate a credit application",
            "GET /api/clients/<applicant_id>/history": "Get client application history",
            "GET /api/stats": "Get database statistics",
            "GET /api/health": "Health check"
        }
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_exists = os.path.exists(DB_PATH)
        
        # Check Qdrant connection using vector_store module
        try:
            collection_info = get_collection_info()
            collection_exists = collection_info["exists"]
            vectors_count = collection_info["vectors_count"]
        except Exception:
            collection_exists = False
            vectors_count = 0
        
        # Check Gemini LLM
        from config import GOOGLE_API_KEY
        llm_status = "configured" if GOOGLE_API_KEY else "not_configured"
        
        if db_exists:
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "vector_store": "connected" if collection_exists else "initializing",
                "llm": llm_status,
                "vectors_count": vectors_count
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "database": "missing",
                "vector_store": "connected" if collection_exists else "disconnected",
                "llm": llm_status
            }), 503
            
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503


@app.route("/api/evaluate", methods=["POST"])
def evaluate_application():
    """
    Evaluate a new credit application
    
    Body (JSON):
    {
        "requested_amount": 15000,
        "annual_income_snapshot": 60000,
        "dti_snapshot": 18.5,
        "fico_snapshot": 720,
        ...
    }
    
    Returns:
        Decision with confidence, reason, and conditions
    """
    
    try:
        new_app = request.json
        
        # Validate required fields
        required = [
            "requested_amount",
            "annual_income_snapshot",
            "dti_snapshot",
            "fico_snapshot"
        ]
        
        missing = [field for field in required if field not in new_app]
        
        if missing:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing,
                "required_fields": required
            }), 400
        
        # Find twins and make decision
        decision = find_twins(new_app)
        
        return jsonify(decision), 200
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route("/api/clients/<applicant_id>/history", methods=["GET"])
def get_client_history(applicant_id):
    """
    Get complete client history
    
    Args:
        applicant_id: Unique client ID
    
    Returns:
        Client profile + list of all applications
    """
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get client profile
        cursor.execute("SELECT * FROM clients WHERE applicant_id = ?", (applicant_id,))
        client = cursor.fetchone()
        
        if not client:
            return jsonify({"error": "Client not found"}), 404
        
        # Get all applications
        cursor.execute("""
            SELECT * FROM applications
            WHERE applicant_id = ?
            ORDER BY application_date DESC
        """, (applicant_id,))
        
        applications = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "client": dict(client),
            "applications": applications,
            "total_applications": len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Global database statistics
    
    Returns:
        Number of clients, applications, outcome distribution
    """
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        total_applications = cursor.fetchone()[0]
        
        # Outcome distribution
        cursor.execute("""
            SELECT outcome_category, COUNT(*) as count
            FROM applications
            GROUP BY outcome_category
        """)
        outcomes = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average requested amount
        cursor.execute("SELECT AVG(requested_amount) FROM applications")
        avg_amount = cursor.fetchone()[0]
        
        # Average FICO
        cursor.execute("SELECT AVG(fico_snapshot) FROM applications")
        avg_fico = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "total_clients": total_clients,
            "total_applications": total_applications,
            "outcome_distribution": outcomes,
            "average_requested_amount": round(avg_amount, 2) if avg_amount else None,
            "average_fico_score": round(avg_fico, 2) if avg_fico else None
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CreditTwin API Server".center(70))
    print("=" * 70)
    print(f"\n🚀 Starting server...")
    print(f"📍 Running on http://localhost:5000")
    print(f"\n📚 API Documentation:")
    print(f"   GET  /              - API information")
    print(f"   GET  /api/health    - Health check")
    print(f"   POST /api/evaluate  - Evaluate credit application")
    print(f"   GET  /api/stats     - Database statistics")
    print(f"\n💡 Press CTRL+C to stop\n")
    
    app.run(debug=False, host="0.0.0.0", port=5000)