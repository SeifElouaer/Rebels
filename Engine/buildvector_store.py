"""
build_vector_store.py
---------------------
Script to build the Qdrant vector store from loan_requests.json

This script orchestrates the vector store creation by:
1. Loading application data
2. Generating embeddings
3. Upserting to Qdrant
"""

import json
import os
import sys
from config import VECTOR_SIZE
from embeddings import create_application_vector
from vector_store import (
    create_collection_if_not_exists,
    batch_upsert_vectors,
    delete_collection,
    get_collection_info
)

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def build_qdrant_vectors(reset_collection: bool = True):
    """
    Load loan_requests.json and create the Qdrant collection
    
    Steps:
    1. Load JSON of applications with known outcomes
    2. Create/reset Qdrant collection
    3. Vectorize each application
    4. Upload in batches to Qdrant
    
    Args:
        reset_collection: If True, delete existing collection before building
    """
    
    print("📥 Loading loan_requests.json...")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(BASE_DIR, "Engine", "loan_requests.json")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"{json_path} not found. Run Engine/data_loader.py first."
        )
    
    with open(json_path, "r") as f:
        applications = json.load(f)
    
    print(f"   Found {len(applications):,} applications")
    
    # Reset collection if requested
    if reset_collection:
        print("🗑️  Resetting collection...")
        delete_collection()
    
    # Create collection
    print("🔧 Creating collection...")
    created = create_collection_if_not_exists()
    if created:
        print("   ✓ Collection created")
    else:
        print("   ✓ Collection already exists")
    
    # Prepare points data
    print("🔢 Vectorizing applications...")
    points_data = []
    
    for idx, app in enumerate(applications):
        # Create vector using embeddings module
        vector = create_application_vector(app, vector_size=VECTOR_SIZE)
        
        # Prepare payload
        payload = {
            # Identifiers
            "application_id": app["application_id"],
            "applicant_id": app["applicant_id"],
            "application_date": app["application_date"],
            
            # Loan parameters
            "requested_amount": float(app["requested_amount"]) if app["requested_amount"] else None,
            "loan_purpose": app["loan_purpose"],
            "term": app["term"],
            "grade": app["grade"],
            
            # Financial snapshot
            "annual_income": float(app["annual_income_snapshot"]) if app["annual_income_snapshot"] else None,
            "dti": float(app["dti_snapshot"]) if app["dti_snapshot"] else None,
            "fico": float(app["fico_snapshot"]) if app["fico_snapshot"] else None,
            
            # Client history
            "nb_previous_loans": int(app["nb_previous_loans"]) if app["nb_previous_loans"] is not None else 0,
            "credit_history_length": float(app["credit_history_length_snapshot"]) if app["credit_history_length_snapshot"] else None,
            
            # Ratios
            "payment_to_income": float(app["payment_to_income_ratio"]) if app["payment_to_income_ratio"] else None,
            "loan_to_income": float(app["loan_to_income_ratio"]) if app["loan_to_income_ratio"] else None,
            
            # Outcome (what we predict)
            "outcome": app["outcome_category"],
            "loan_status": app["loan_status"],
            "was_successful": app["outcome_category"] == "success",
            "defaulted": app["outcome_category"] == "default",
            "had_late_payments": app["outcome_category"] == "late_payments",
            
            # Advanced Insights
            "is_fraud_suspect": bool(app.get("is_fraud_suspect", 0)),
            "is_comeback_story": bool(app.get("is_comeback_story", 0)),
        }
        
        points_data.append((idx, vector, payload))
    
    # Upload in batches using vector_store module
    print("📤 Uploading to Qdrant (batch_size=1000)...")
    total_uploaded = batch_upsert_vectors(points_data, batch_size=1000)
    
    # Verify
    info = get_collection_info()
    print(f"✅ Vector store built successfully")
    print(f"   - Total vectors: {info['vectors_count']:,}")
    print(f"   - Vector size: {info['config']['vector_size']}")
    print(f"   - Distance metric: {info['config']['distance']}")


if __name__ == "__main__":
    print("=" * 70)
    print("CreditTwin Vector Store Builder".center(70))
    print("=" * 70)
    
    try:
        build_qdrant_vectors(reset_collection=True)
        
        print("=" * 70)
        print("✅ Vector store built successfully".center(70))
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise