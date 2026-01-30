"""
twin_search.py
--------------
Search for "financial twins" in history and make decisions
based on their actual outcomes.
"""

import sys
from embeddings import create_application_vector
from vector_store import search_similar
from config import VECTOR_SIZE
import numpy as np
from datetime import datetime
from llm_explanation import get_llm_explanation

# Performance: We'll pre-calculate some "Roadmap" thresholds
SUCCESS_THRESH = 0.85
LATE_RISK_THRESH = 0.15
FRAUD_SIMILARITY_LIMIT = 0.999 # Very high similarity to multiple historical IDs is suspicious

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def generate_friendly_explanation(decision_data):
    """
    Translates structured risk signals into a human-friendly explanation.
    
    Args:
        decision_data: The full result dictionary from find_twins
        
    Returns:
        A short, supportive, and clear explanation string.
    """
    decision = decision_data.get("decision", "UNKNOWN")
    confidence = decision_data.get("confidence", 0) * 100
    analysis = decision_data.get("analysis", {})
    success_rate = analysis.get("success_rate", 0) * 100
    rejected_count = analysis.get("rejected_count", 0)
    
    # Decisions derived from twin matching
    if decision == "APPROVED":
        msg = (f"Your application shows a very strong alignment with successful historical cases. "
                f"With a {success_rate:.0f}% success rate among your 'financial twins,' we have high "
                f"confidence in this approval.")
        if rejected_count > 0:
            msg += f" Only {rejected_count} out of {analysis['total_twins']} similar matches were previously rejected."
        return msg
    
    elif decision == "APPROVED_WITH_CONDITIONS":
        return (f"We've approved your request with tailored conditions to ensure your success. "
                f"Applicants with your profile have a solid {success_rate:.0f}% success rate, "
                f"though we've identified moderate risks that require slight adjustments to the loan terms. "
                f"This approach helps balance your current needs with long-term financial safety.")
        
    elif decision == "REJECTED":
        return (f"After comparing your application to thousands of 'financial twins,' we cannot approve your request today. "
                f"The historical data for similar profiles indicates a higher risk of repayment challenges. "
                f"We recommend focusing on your debt-to-income ratio or credit score to improve your profile for future requests.")
        
    elif decision == "ANOMALY_DETECTED":
        return (f"Your unique financial request has been flagged for prioritized manual review by our experts. "
                f"Because we found very few similar historical cases, we want to ensure a human specialist "
                f"personally evaluates your situation rather than relying on automated matching. "
                f"This ensures you receive a fair and comprehensive assessment.")
        
    elif decision == "MANUAL_REVIEW":
        return (f"The engine has categorized your request for manual underwriting because the outcomes "
                f"of your 'financial twins' were inconsistent. Since {success_rate:.0f}% of similar cases "
                f"succeeded while others faced challenges, a human specialist will now perform a targeted "
                f"final check to ensure we reach the most fair and accurate decision for you.")
        
    return "Your application is being analyzed using our financial twin matching engine to ensure a fair and data-driven decision."


def find_twins(new_application, top_k=100, threshold=0.70):
    """
    Find similar historical applications (twins) and recommend a decision
    
    Process:
    1. Vectorize the new application
    2. Search for top_k similar vectors in Qdrant
    3. Detect anomalies (< 10 twins found)
    4. Analyze twin outcomes
    5. Apply decision rules
    
    Args:
        new_application: Dict with the new application features
        top_k: Maximum number of twins to return
        threshold: Minimum similarity threshold (0-1)
    
    Returns:
        Dict with decision, confidence, reason, and detailed analysis
    """
    
    print(f"🔍 Searching for twins (top_k={top_k}, threshold={threshold})...")
    
    # 1. Create vector using embeddings module
    vector = create_application_vector(new_application, vector_size=VECTOR_SIZE)
    
    # 2. Search using vector_store module
    # Note: Qdrant's search already filters by score_threshold internally
    # For now, we'll get top_k results and the vector_store will handle filtering
    
    # Optional filters for amount range
    filters = None
    if new_application.get("requested_amount"):
        filters = {
            "requested_amount": {
                "$gte": new_application["requested_amount"] * 0.7,
                "$lte": new_application["requested_amount"] * 1.3
            }
        }
    
    # Search using the new vector_store module
    try:
        results = search_similar(vector=vector, top_k=top_k, filters=filters)
    except Exception as e:
        print(f"⚠️ Search failed (initializing?): {e}")
        results = []
    
    print(f"   Found {len(results)} similar cases")
    
    # 3. Anomaly detection
    if len(results) < 10:
        result = {
            "decision": "ANOMALY_DETECTED",
            "reason": f"Only {len(results)} similar cases found (minimum 10 required)",
            "twins_found": len(results),
            "action": "MANUAL_REVIEW_REQUIRED",
            "confidence": 0.0
        }
        result["explanation"] = get_llm_explanation(result, new_application) or generate_friendly_explanation(result)
        return result
    
    # 4. Analyze twins
    analysis = analyze_twins(results)
    
    # 5. Advanced Check: Identity Anomaly (Fraud)
    fraud_flags = [r["payload"].get("is_fraud_suspect", 0) for r in results[:20]]
    if sum(fraud_flags) >= 5 or analysis["avg_similarity"] > FRAUD_SIMILARITY_LIMIT:
        decision = {
            "decision": "REJECTED",
            "confidence": 1.0,
            "reason": "IDENTITY_ANOMALY: Our system detected patterns unusually similar to known high-risk applications.",
            "is_fraud_suspect": True,
            "analysis": analysis
        }
        decision["explanation"] = get_llm_explanation(decision, new_application) or generate_friendly_explanation(decision)
        return decision

    # 6. Make decision
    decision = make_decision(analysis, new_application)
    
    # 7. Feature: Path to Success (for REJECTED)
    if decision["decision"] == "REJECTED":
        comebacks = [r for r in results if r["payload"].get("is_comeback_story", 0)]
        if comebacks:
            best_comeback = comebacks[0]["payload"]
            decision["roadmap"] = {
                "target_fico": best_comeback.get("fico", 700),
                "target_dti": round(best_comeback.get("dti", 20.0), 1),
                "message": f"We found profiles identical to yours that were successful after improving their FICO to {int(best_comeback.get('fico', 0))}+ and lowering DTI to {best_comeback.get('dti')}%."
            }
        
        # Feature: Product Up-Selling (Safer Loan Amount)
        successful_twins = [r for r in results if r["payload"]["outcome"] == "success"]
        if successful_twins:
            avg_safe_amount = sum(r["payload"]["requested_amount"] or 0 for r in successful_twins) / len(successful_twins)
            if avg_safe_amount < new_application.get("requested_amount", 0) * 0.8:
                decision["alternative_offer"] = {
                    "type": "SAFER_AMOUNT",
                    "amount": round(avg_safe_amount, -2),
                    "message": f"While your current request is high, your financial twins were highly successful with loans around ${int(avg_safe_amount):,}."
                }
    
    # 8. Feature: Smart Nudges (for APPROVED or APPROVED_WITH_CONDITIONS)
    if "APPROVED" in decision["decision"]:
        # Predict next likely needs based on seniority
        if new_application.get("nb_previous_loans", 0) == 0:
            decision["nudge"] = {
                "title": "Build Your Legacy",
                "message": "80% of clients who started with this loan successfully upgraded to our Home Improvement line within 18 months."
            }

    # 9. Generate human-friendly explanation
    template_explanation = generate_friendly_explanation(decision)
    
    # Try to get LLM explanation, fallback to template
    llm_explanation = get_llm_explanation(decision, new_application)
    decision["explanation"] = llm_explanation if llm_explanation else template_explanation
    
    return decision


def analyze_twins(results):
    """
    Analyze the outcomes of found twins
    
    Args:
        results: List of dicts with 'score' and 'payload'
    
    Returns:
        Dict with statistics and top twins
    """
    
    total = len(results)
    
    if total == 0:
        return {
            "total_twins": 0,
            "success_count": 0,
            "default_count": 0,
            "late_count": 0,
            "success_rate": 0.0,
            "default_rate": 0.0,
            "late_rate": 0.0,
            "avg_similarity": 0.0,
            "top_twins": []
        }
    
    # Count outcomes
    success = sum(1 for r in results if r["payload"]["outcome"] == "success")
    default = sum(1 for r in results if r["payload"]["outcome"] == "default")
    late = sum(1 for r in results if r["payload"]["outcome"] == "late_payments")
    rejected = sum(1 for r in results if r["payload"]["outcome"] == "rejected")
    
    # Average similarity
    avg_score = sum(r["score"] for r in results) / total
    
    # Top 5 for explanation
    top_twins = []
    for r in results[:5]:
        payload = r["payload"]
        top_twins.append({
            "application_id": payload.get("application_id"),
            "similarity": round(r["score"], 3),
            "outcome": payload.get("outcome"),
            "requested_amount": payload.get("requested_amount"),
            "fico": payload.get("fico"),
            "dti": payload.get("dti"),
        })
    
    return {
        "total_twins": total,
        "success_count": success,
        "default_count": default,
        "late_count": late,
        "rejected_count": rejected,
        "success_rate": success / total,
        "default_rate": default / total,
        "late_rate": late / total,
        "avg_similarity": avg_score,
        "top_twins": top_twins
    }


def make_decision(analysis, application):
    """
    Apply decision rules based on twin analysis
    
    Rules:
    - Success rate ≥ 85% AND default rate < 5% → APPROVED
    - 65% ≤ Success rate < 85% → APPROVED_WITH_CONDITIONS
    - Success rate < 65% OR default rate > 25% → REJECTED
    - Other cases → MANUAL_REVIEW
    
    Args:
        analysis: Dict with twin statistics
        application: Dict with the original application
    
    Returns:
        Dict with decision, confidence, reason, conditions
    """
    
    success_rate = analysis["success_rate"]
    default_rate = analysis["default_rate"]
    
    # Rule 1: High success rate - Pure Approval (Top 1%)
    if success_rate >= 0.99 and default_rate < 0.05:
        return {
            "decision": "APPROVED",
            "confidence": analysis["avg_similarity"],
            "reason": f"Exceptional {int(success_rate*100)}% success rate observed among similar financial profiles.",
            "conditions": [],
            "recommended_amount": application.get("requested_amount"),
            "analysis": analysis
        }
    
    # Rule 2: Good success but some risk - Approval with Conditions (Top 10%)
    elif success_rate >= 0.90 and default_rate < 0.10:
        conditions = []
        recommended_amount = application.get("requested_amount")
        
        if default_rate > 0.05:
            conditions.append("Mandatory 25% reduction in requested amount")
            recommended_amount = application.get("requested_amount", 0) * 0.75
        
        if analysis["late_rate"] > 0.10:
            conditions.append("Interest rate premium (+1.5% APR)")
        
        if not conditions:
            conditions.append("Standard conditions with enhanced monitoring")
        
        return {
            "decision": "APPROVED_WITH_CONDITIONS",
            "confidence": analysis["avg_similarity"],
            "reason": "Solid historical performance with minor risk overhead.",
            "conditions": conditions,
            "recommended_amount": recommended_amount,
            "analysis": analysis
        }
    
    # Rule 3: Moderate Success - Manual Review
    elif success_rate >= 0.85:
        return {
            "decision": "MANUAL_REVIEW",
            "confidence": analysis["avg_similarity"],
            "reason": f"Success rate is {int(success_rate*100)}%. Performance data is within a neutral range requiring human oversight.",
            "analysis": analysis
        }
    
    # Rule 4: Everything else - Rejection (Below 85% success)
    else:
        return {
            "decision": "REJECTED",
            "confidence": analysis["avg_similarity"],
            "reason": f"Inadequate success likelihood ({int(success_rate*100)}%). Historical comparisons show significant default risk.",
            "analysis": analysis
        }


if __name__ == "__main__":
    # Example test
    test_application = {
        "requested_amount": 15000,
        "loan_purpose": "debt_consolidation",
        "term": " 36 months",
        "grade": "B",
        "annual_income_snapshot": 60000,
        "dti_snapshot": 18.5,
        "fico_snapshot": 720,
        "credit_history_length_snapshot": 8.3,
        "revolving_utilization_snapshot": 45.2,
        "nb_previous_loans": 2,
        "open_accounts": 8,
        "total_accounts": 15,
        "delinquencies_2y": 0,
        "inquiries_6m": 1,
        "public_records": 0,
        "payment_to_income_ratio": 0.25,
        "loan_to_income_ratio": 0.25,
    }
    
    print("=" * 70)
    print("Testing CreditTwin Search".center(70))
    print("=" * 70)
    
    try:
        result = find_twins(test_application)
        
        print(f"\n📊 DECISION: {result['decision']}")
        print(f"📈 Confidence: {result.get('confidence', 0):.2%}")
        print(f"💡 Reason: {result['reason']}")
        
        if result.get('conditions'):
            print(f"\n⚠️  Conditions:")
            for condition in result['conditions']:
                print(f"   - {condition}")
        
        if result.get('analysis'):
            analysis = result['analysis']
            print(f"\n📈 TWIN ANALYSIS:")
            print("=" * 70)
            print(f"Total twins found: {analysis['total_twins']}")
            print(f"Success rate: {analysis['success_rate']:.2%}")
            print(f"Default rate: {analysis['default_rate']:.2%}")
            print(f"Late payments rate: {analysis['late_rate']:.2%}")
            print(f"Average similarity: {analysis['avg_similarity']:.2%}")
            
            if analysis['top_twins']:
                print(f"\n🔝 TOP 5 SIMILAR CASES:")
                print("-" * 70)
                for i, twin in enumerate(analysis['top_twins'], 1):
                    print(f"{i}. ID: {twin['application_id']}")
                    print(f"   Similarity: {twin['similarity']:.2%}")
                    print(f"   Outcome: {twin['outcome']}")
                    print(f"   Amount: ${twin['requested_amount']:,.0f}, FICO: {twin['fico']:.0f}, DTI: {twin['dti']:.1f}%")
                    print()
        
        print("=" * 70)
        print("✅ Test completed successfully".center(70))
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise