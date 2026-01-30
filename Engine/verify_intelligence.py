import requests
import json
import sys

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

API_URL = "http://localhost:5000/api/evaluate"

scenarios = [
    {
        "name": "1. Golden Profile (Success + Nudge)",
        "payload": {
            "requested_amount": 10000, "annual_income_snapshot": 90000, "fico_snapshot": 790, "monthly_debt": 400,
            "loan_purpose": "credit_card", "term": " 36 months", "nb_previous_loans": 0
        }
    },
    {
        "name": "2. High Debt (Reject + Roadmap)",
        "payload": {
            "requested_amount": 10000, "annual_income_snapshot": 30000, "fico_snapshot": 520, "monthly_debt": 2000,
            "loan_purpose": "debt_consolidation", "term": " 36 months", "nb_previous_loans": 0
        }
    },
    {
        "name": "3. Over-Leveraged (Reject + Alternative Offer)",
        "payload": {
            "requested_amount": 75000, "annual_income_snapshot": 45000, "fico_snapshot": 700, "monthly_debt": 500,
            "loan_purpose": "home_improvement", "term": " 60 months", "nb_previous_loans": 0
        }
    },
    {
        "name": "4. Identity Anomaly (Fraud Check)",
        "payload": {
            "requested_amount": 25000, "annual_income_snapshot": 150000, "fico_snapshot": 820, "monthly_debt": 0,
            "loan_purpose": "other", "term": " 36 months", "nb_previous_loans": 0
        }
    }
]

def run_tests():
    print("=" * 70)
    print("CreditTwin Intelligence Verification".center(70))
    print("=" * 70)

    for s in scenarios:
        print(f"\n🚀 Testing: {s['name']}")
        try:
            # Prepare payload (calc DTI if missing)
            p = s['payload'].copy()
            if 'dti_snapshot' not in p and p.get('annual_income_snapshot', 0) > 0:
                monthly_inc = p['annual_income_snapshot'] / 12
                p['dti_snapshot'] = (p.get('monthly_debt', 0) / monthly_inc) * 100

            r = requests.post(API_URL, json=p)
            r.raise_for_status()
            res = r.json()
            
            print(f"   Decision: {res.get('decision')}")
            if res.get('analysis'):
                print(f"   Success Rate: {res['analysis']['success_rate']*100:.1f}%")
            
            # Check for features
            if res.get('nudge'): print(f"   ✅ [Nudge] found: {res['nudge']['title']}")
            if res.get('roadmap'): print(f"   ✅ [Roadmap] found: {res['roadmap']['message']}")
            if res.get('alternative_offer'): print(f"   ✅ [Offer] found: {res['alternative_offer']['message']}")
            if res.get('is_fraud_suspect'): print(f"   ✅ [Fraud Alert] Triggered")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    run_tests()
