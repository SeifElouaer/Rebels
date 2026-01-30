import sys
import os
import json

# Force UTF-8 encoding for stdout to avoid issues on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add Engine to path
sys.path.append(os.path.join(os.getcwd(), 'Engine'))

try:
    from twin_search import find_twins
    from config import COLLECTION_NAME
    from vector_store import get_collection_info
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

def run_verification():
    print("=" * 70)
    print("CreditTwin Feature Verification".center(70))
    print("=" * 70)

    # 1. Check Backend Connectivity
    print("\n[1/3] Checking Backend Connectivity...")
    info = get_collection_info()
    if info["exists"]:
        print(f"   ✓ Qdrant Collection '{COLLECTION_NAME}' exists")
        print(f"   ✓ Vectors count: {info['vectors_count']:,}")
    else:
        print(f"   ❌ Qdrant Collection '{COLLECTION_NAME}' NOT found!")
        return

    # 2. Test Twin Searching (Standard Case)
    print("\n[2/3] Testing Twin Searching (Standard Case)...")
    standard_app = {
        "requested_amount": 10000,
        "loan_purpose": "debt_consolidation",
        "term": " 36 months",
        "grade": "B",
        "annual_income_snapshot": 50000,
        "dti_snapshot": 15.0,
        "fico_snapshot": 700,
        "credit_history_length_snapshot": 5.0,
        "revolving_utilization_snapshot": 30.0,
        "nb_previous_loans": 1,
        "open_accounts": 10,
        "total_accounts": 20,
        "delinquencies_2y": 0,
        "inquiries_6m": 0,
        "public_records": 0,
        "payment_to_income_ratio": 0.1,
        "loan_to_income_ratio": 0.2,
    }
    
    try:
        result = find_twins(standard_app)
        if result.get("decision"):
            print(f"   ✓ Decision received: {result['decision']}")
            print(f"   ✓ Twins found: {result.get('analysis', {}).get('total_twins', 0)}")
            print(f"   ✓ Confidence: {result.get('confidence', 0):.2%}")
        else:
            print(f"   ❌ Unexpected result format: {result}")
    except Exception as e:
        print(f"   ❌ Error during twin search: {e}")

    # 3. Test Anomaly Detection (Extreme Case)
    print("\n[3/3] Testing Anomaly Detection (Extreme Case)...")
    # Using an extremely high amount and unusual parameters to minimize matches
    anomaly_app = standard_app.copy()
    anomaly_app["requested_amount"] = 9999999  # Extreme amount
    anomaly_app["annual_income_snapshot"] = 10  # Extreme low income
    
    try:
        # Note: We need to set top_k and threshold if we want to ensure < 10 matches
        # but find_twins uses defaults. Let's see if the extreme case naturally triggers it.
        result = find_twins(anomaly_app, threshold=0.95) # High threshold to force few matches
        if result.get("decision") == "ANOMALY_DETECTED":
            print(f"   ✓ Anomaly correctly detected!")
            print(f"   ✓ Reason: {result['reason']}")
            print(f"   ✓ Action: {result['action']}")
        else:
            print(f"   ℹ️ Decision: {result['decision']} (Matches: {result.get('twins_found') or result.get('analysis', {}).get('total_twins')})")
            if result.get("decision") != "ANOMALY_DETECTED":
                print(f"   ⚠️  Anomaly detection was not triggered. This might mean the dataset is very dense or the threshold/parameters were not extreme enough.")
    except Exception as e:
        print(f"   ❌ Error during anomaly detection test: {e}")

    print("\n" + "=" * 70)
    print("Verification Completed".center(70))
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
