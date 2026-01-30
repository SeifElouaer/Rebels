"""
CreditTwin Business Logic Services
This module contains placeholder functions for the credit decision engine.
The actual implementation will be added later.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from models import (
    CreditApplication, FinancialTwin, AnomalyFlag, 
    DecisionResult, CreditDecisionResponse, DatabaseStats
)

# In-memory storage for historical cases (will be replaced by Qdrant)
historical_cases: List[Dict[str, Any]] = []

# Constants
EMPLOYMENT_TYPES = ['full-time', 'part-time', 'self-employed', 'contractor', 'retired']
SECTORS = ['technology', 'healthcare', 'finance', 'retail', 'manufacturing', 'education', 'government', 'other']
PURPOSES = ['home', 'auto', 'personal', 'business', 'education', 'debt-consolidation']
REGIONS = ['northeast', 'southeast', 'midwest', 'southwest', 'west']


def get_historical_cases() -> List[Dict[str, Any]]:
    """Get all historical cases"""
    return historical_cases


def set_historical_cases(cases: List[Dict[str, Any]]) -> None:
    """Set historical cases"""
    global historical_cases
    historical_cases = cases


def clear_historical_cases() -> None:
    """Clear all historical cases"""
    global historical_cases
    historical_cases = []


def get_case_count() -> int:
    """Get total number of cases"""
    return len(historical_cases)


def generate_historical_case(case_id: int) -> Dict[str, Any]:
    """Generate a single synthetic historical case"""
    import random
    
    credit_score = random.randint(450, 850)
    income = random.randint(20000, 200000)
    age = random.randint(22, 72)
    
    # Loan amount relative to income, but with some randomness
    loan_amount = random.randint(5000, int(income * 2))
    
    debt = int(random.uniform(0, 0.5) * income)
    assets = int(random.uniform(0, 3) * income)
    
    tenure_options = [12, 24, 36, 48, 60, 72]
    tenure = random.choice(tenure_options)
    
    if credit_score > 700:
        delinquencies = random.randint(0, 1)
    else:
        delinquencies = random.randint(0, 4)
        
    utilization = random.randint(5, 85)
    history_length = random.randint(1, 20)
    
    # Calculate risk factors for outcome generation
    dti = debt / income if income > 0 else 0
    lti = loan_amount / income if income > 0 else 0
    
    # Base probability of default
    default_prob = 0.1
    
    if credit_score < 600: default_prob += 0.25
    elif credit_score < 680: default_prob += 0.1
    
    if dti > 0.4: default_prob += 0.15
    if lti > 1.5: default_prob += 0.1
    if delinquencies > 2: default_prob += 0.2
    if utilization > 70: default_prob += 0.1
    
    is_default = random.random() < default_prob
    
    # Days late based on default status
    if is_default:
        days_late = random.randint(30, 210)
        outcome = 'DEFAULTED'
    else:
        # Some repaid loans might have been late successfully cured
        if random.random() < 0.2:
            days_late = random.randint(1, 29)
        else:
            days_late = 0
        outcome = 'REPAID'
        
    # Decision logic for the historical record (hindsight)
    # If it defaulted, we might have declined it if we knew better, 
    # but for historical training data, we assume these were approved loans.
    # However, to make the data realistic, we mark some as "would decline" if re-evaluated.
    decision = 'APPROVED'
    
    return {
        'id': f'LOAN_{str(case_id).zfill(5)}',
        'borrower_id': f'BRW_{str(random.randint(1, 100000)).zfill(5)}',
        'age': age,
        'credit_score': credit_score,
        'income': income,
        'debt': debt,
        'assets': assets,
        'loan_amount': loan_amount,
        'tenure': tenure,
        'employment': random.choice(EMPLOYMENT_TYPES),
        'sector': random.choice(SECTORS),
        'purpose': random.choice(PURPOSES),
        'region': random.choice(REGIONS),
        'delinquencies': delinquencies,
        'utilization': utilization,
        'history_length': history_length,
        'decision': decision,
        'outcome': outcome,
        'days_late': days_late
    }


def generate_synthetic_data(count: int = 1000) -> List[Dict[str, Any]]:
    """Generate a batch of synthetic data"""
    return [generate_historical_case(i + 1) for i in range(count)]


# Initialize with synthetic data
historical_cases: List[Dict[str, Any]] = generate_synthetic_data(1000)


def get_sample_cases(count: int = 20) -> List[Dict[str, Any]]:
    """Get a random sample of cases for display"""
    if len(historical_cases) == 0:
        return []
    
    import random
    sample_size = min(count, len(historical_cases))
    return random.sample(historical_cases, sample_size)


def get_database_stats() -> DatabaseStats:
    """Calculate database statistics"""
    if len(historical_cases) == 0:
        return DatabaseStats(
            total=0,
            repaid=0,
            defaulted=0,
            purpose_counts={p: 0 for p in PURPOSES}
        )
    
    df = pd.DataFrame(historical_cases)
    
    repaid = len(df[df['outcome'] == 'REPAID']) if 'outcome' in df.columns else 0
    defaulted = len(df[df['outcome'] == 'DEFAULTED']) if 'outcome' in df.columns else 0
    
    purpose_counts = {p: 0 for p in PURPOSES}
    if 'purpose' in df.columns:
        counts = df['purpose'].value_counts().to_dict()
        for p in PURPOSES:
            purpose_counts[p] = counts.get(p, 0)
    
    return DatabaseStats(
        total=len(historical_cases),
        repaid=repaid,
        defaulted=defaulted,
        purpose_counts=purpose_counts
    )


# ============================================================================
# PLACEHOLDER FUNCTIONS - TO BE IMPLEMENTED WITH ACTUAL CREDIT DECISION ENGINE
# ============================================================================

def normalize_feature(value: float, min_val: float, max_val: float) -> float:
    """Normalize a feature to 0-1 range"""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def create_feature_vector(applicant: Dict[str, Any]) -> np.ndarray:
    """
    Create a feature vector from applicant data.
    """
    # Helper to safely get numeric values
    def get_num(key, default=0):
        val = applicant.get(key, default)
        try:
            return float(val)
        except:
            return float(default)

    vector = [
        normalize_feature(get_num('age', 35), 18, 80),
        normalize_feature(get_num('credit_score', 650), 300, 850),
        normalize_feature(get_num('income', 50000), 10000, 500000),
        normalize_feature(get_num('debt', 0), 0, 300000),
        normalize_feature(get_num('assets', 0), 0, 2000000),
        normalize_feature(get_num('loan_amount', 10000), 1000, 500000),
        normalize_feature(get_num('tenure', 36), 6, 84),
        normalize_feature(get_num('delinquencies', 0), 0, 12),
        normalize_feature(get_num('utilization', 30), 0, 100),
        normalize_feature(get_num('history_length', 5), 0, 50),
        
        # Categorical encodings
        EMPLOYMENT_TYPES.index(map_categorical(applicant.get('employment'), EMPLOYMENT_TYPES)) / len(EMPLOYMENT_TYPES),
        SECTORS.index(map_categorical(applicant.get('sector'), SECTORS)) / len(SECTORS),
        PURPOSES.index(map_categorical(applicant.get('purpose'), PURPOSES)) / len(PURPOSES),
        REGIONS.index(map_categorical(applicant.get('region'), REGIONS)) / len(REGIONS),
    ]
    return np.array(vector)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def find_financial_twins(applicant: Dict[str, Any], k: int = 50) -> List[FinancialTwin]:
    """
    Find the k most similar historical cases.
    
    PLACEHOLDER: This will be replaced with actual Qdrant vector search.
    Currently uses simple cosine similarity on feature vectors.
    """
    if len(historical_cases) == 0:
        return []
    
    applicant_vector = create_feature_vector(applicant)
    
    similarities = []
    for case in historical_cases:
        case_vector = create_feature_vector(case)
        similarity = cosine_similarity(applicant_vector, case_vector)
        similarities.append((case, similarity))
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k as FinancialTwin objects
    twins = []
    for case, similarity in similarities[:k]:
        twins.append(FinancialTwin(
            id=case.get('id', 'UNKNOWN'),
            borrower_id=case.get('borrower_id', 'UNKNOWN'),
            age=case.get('age', 0),
            credit_score=case.get('credit_score', 0),
            income=case.get('income', 0),
            debt=case.get('debt', 0),
            assets=case.get('assets', 0),
            loan_amount=case.get('loan_amount', 0),
            tenure=case.get('tenure', 0),
            employment=case.get('employment', 'unknown'),
            sector=case.get('sector', 'unknown'),
            purpose=case.get('purpose', 'unknown'),
            region=case.get('region', 'unknown'),
            decision=case.get('decision', 'UNKNOWN'),
            outcome=case.get('outcome', 'UNKNOWN'),
            days_late=case.get('days_late', 0),
            similarity=similarity
        ))
    
    return twins


def calculate_anomaly_score(twins: List[FinancialTwin]) -> float:
    """
    Calculate anomaly score based on similarity distribution.
    """
    if len(twins) == 0:
        return 1.0
    
    max_sim = twins[0].similarity
    avg_sim = sum(t.similarity for t in twins) / len(twins)
    
    # Calculate decay rate
    if len(twins) >= 10 and max_sim > 0:
        decay_rate = (twins[0].similarity - twins[min(9, len(twins)-1)].similarity) / max_sim
    else:
        decay_rate = 0.0
    
    # Anomaly components
    anomaly_from_similarity = 1 - max_sim
    anomaly_from_decay = decay_rate
    anomaly_from_density = 1 - avg_sim
    
    # Combined anomaly score
    anomaly_score = (
        anomaly_from_similarity * 0.4 +
        anomaly_from_decay * 0.3 +
        anomaly_from_density * 0.3
    )
    
    return min(1.0, max(0.0, anomaly_score))


def detect_anomaly_flags(applicant: Dict[str, Any]) -> List[AnomalyFlag]:
    """
    Detect specific anomaly patterns in the application.
    """
    flags = []
    
    income = float(applicant.get('income', 0))
    credit_score = float(applicant.get('credit_score', 0))
    loan_amount = float(applicant.get('loan_amount', 0))
    debt = float(applicant.get('debt', 0))
    assets = float(applicant.get('assets', 0))
    utilization = float(applicant.get('utilization', 0))
    delinquencies = float(applicant.get('delinquencies', 0))
    history_length = float(applicant.get('history_length', 0))
    
    # High income with low credit score
    if income > 150000 and credit_score < 600:
        flags.append(AnomalyFlag(
            type='warning',
            text='High income but low credit score - unusual combination'
        ))
    
    # High loan amount for thin file
    if loan_amount > income * 2 and history_length < 3:
        flags.append(AnomalyFlag(
            type='warning',
            text='Large loan request with thin credit history'
        ))
    
    # High utilization with high assets
    if utilization > 80 and assets > 500000:
        flags.append(AnomalyFlag(
            type='info',
            text='High utilization despite significant assets'
        ))
        
    # Recent delinquencies with good score
    if delinquencies > 3 and credit_score > 700:
        flags.append(AnomalyFlag(
            type='warning',
            text='Recent delinquencies inconsistent with credit score'
        ))
    
    # High DTI ratio
    dti = debt / income if income > 0 else 0
    if dti > 0.5:
        flags.append(AnomalyFlag(
            type='alert',
            text=f'High debt-to-income ratio: {dti * 100:.1f}%'
        ))
    
    return flags


def make_decision(
    twins: List[FinancialTwin], 
    anomaly_score: float, 
    applicant: Dict[str, Any]
) -> DecisionResult:
    """
    Make credit decision based on twins and anomaly analysis.
    """
    # Calculate cohort statistics
    if not twins:
         return DecisionResult(
            decision="DECLINE",
            confidence=0.5,
            risk_tier="HIGH",
            reason="Insufficient historical data to evaluate application",
            default_rate=0.0,
            avg_days_late=0.0,
            repaid_count=0,
            default_count=0
        )

    default_count = sum(1 for t in twins if t.outcome == 'DEFAULTED')
    repaid_count = len(twins) - default_count
    default_rate = default_count / len(twins)
    
    total_days_late = sum(t.days_late for t in twins)
    avg_days_late = total_days_late / len(twins)
    
    # Decision logic
    decision = "CONDITIONAL"
    confidence = 0.65
    risk_tier = "MEDIUM"
    reason = "Mixed signals - manual review recommended"
    
    if default_rate < 0.1 and anomaly_score < 0.3:
        decision = "APPROVE"
        confidence = 0.85 + (1 - default_rate) * 0.1 - anomaly_score * 0.1
        risk_tier = "LOW"
        reason = "Strong cohort performance and typical profile"
        
    elif default_rate < 0.2 and anomaly_score < 0.5:
        decision = "CONDITIONAL"
        confidence = 0.7 + (1 - default_rate) * 0.1 - anomaly_score * 0.1
        risk_tier = "MEDIUM"
        reason = "Moderate risk - additional verification recommended"
        
    elif anomaly_score > 0.6:
        decision = "DECLINE"
        confidence = 0.6 + anomaly_score * 0.3
        risk_tier = "HIGH"
        reason = "Profile significantly different from historical cases"
        
    elif default_rate > 0.25:
        decision = "DECLINE"
        confidence = 0.7 + default_rate * 0.2
        risk_tier = "HIGH"
        reason = "Similar borrowers have high default rates"
    
    return DecisionResult(
        decision=decision,
        confidence=min(0.99, confidence),
        risk_tier=risk_tier,
        reason=reason,
        default_rate=default_rate,
        avg_days_late=avg_days_late,
        repaid_count=repaid_count,
        default_count=default_count
    )


def process_credit_application(application: CreditApplication) -> CreditDecisionResponse:
    """
    Process a credit application and return full decision response.
    
    This is the main entry point for credit decisions.
    """
    # Convert application to dict for processing
    applicant = {
        'age': application.age,
        'credit_score': application.credit_score,
        'income': application.income,
        'debt': application.debt,
        'assets': application.assets,
        'loan_amount': application.loan_amount,
        'tenure': application.tenure,
        'employment': application.employment.value,
        'sector': application.sector.value,
        'purpose': application.purpose.value,
        'region': application.region.value,
    }
    
    # Find financial twins
    twins = find_financial_twins(applicant, k=50)
    
    # Calculate anomaly score
    anomaly_score = calculate_anomaly_score(twins)
    
    # Detect anomaly flags
    flags = detect_anomaly_flags(applicant)
    
    # Make decision
    decision = make_decision(twins, anomaly_score, applicant)
    
    return CreditDecisionResponse(
        twins=twins,
        anomaly_score=anomaly_score,
        flags=flags,
        decision=decision
    )


def map_categorical(value: Any, valid_options: List[str]) -> str:
    """Map a value to valid categorical option"""
    if not value:
        return valid_options[-1]  # Default to last option (usually 'other')
    
    lower_val = str(value).lower().replace('-', '').replace('_', '').replace(' ', '')
    
    for opt in valid_options:
        opt_clean = opt.lower().replace('-', '').replace('_', '').replace(' ', '')
        if lower_val == opt_clean or opt_clean in lower_val or lower_val in opt_clean:
            return opt
    
    return valid_options[-1]


def convert_row_to_case(row: Dict[str, Any], mappings: Dict[str, str], idx: int) -> Dict[str, Any]:
    """Convert a data row to a historical case using column mappings"""
    
    def safe_int(val, default=0):
        try:
            return int(float(val)) if val is not None and str(val).strip() else default
        except:
            return default
    
    def safe_float(val, default=0.0):
        try:
            return float(val) if val is not None and str(val).strip() else default
        except:
            return default
    
    # Parse outcome
    outcome = 'REPAID'
    if mappings.get('outcome'):
        outcome_val = str(row.get(mappings['outcome'], '')).lower()
        if any(x in outcome_val for x in ['default', 'charged', 'late', 'bad', '1', 'true']):
            outcome = 'DEFAULTED'
    
    return {
        'id': f'IMPORT_{str(idx + 1).zfill(6)}',
        'borrower_id': f'BRW_{str(idx + 1).zfill(6)}',
        'age': min(100, max(18, safe_int(row.get(mappings.get('age', ''), 35), 35))),
        'credit_score': min(850, max(300, safe_int(row.get(mappings.get('credit_score', ''), 650), 650))),
        'income': max(0, safe_float(row.get(mappings.get('income', ''), 50000), 50000)),
        'debt': max(0, safe_float(row.get(mappings.get('debt', ''), 0), 0)) if mappings.get('debt') else 0,
        'assets': max(0, safe_float(row.get(mappings.get('assets', ''), 0), 0)) if mappings.get('assets') else 0,
        'loan_amount': max(0, safe_float(row.get(mappings.get('loan_amount', ''), 10000), 10000)),
        'tenure': safe_int(row.get(mappings.get('tenure', ''), 36), 36) if mappings.get('tenure') else 36,
        'employment': map_categorical(row.get(mappings.get('employment', ''), ''), EMPLOYMENT_TYPES) if mappings.get('employment') else 'full-time',
        'sector': map_categorical(row.get(mappings.get('sector', ''), ''), SECTORS) if mappings.get('sector') else 'other',
        'purpose': map_categorical(row.get(mappings.get('purpose', ''), ''), PURPOSES) if mappings.get('purpose') else 'personal',
        'region': map_categorical(row.get(mappings.get('region', ''), ''), REGIONS) if mappings.get('region') else 'northeast',
        'decision': 'DECLINED' if outcome == 'DEFAULTED' else 'APPROVED',
        'outcome': outcome,
        'days_late': safe_int(row.get(mappings.get('days_late', ''), 0), 0) if mappings.get('days_late') else (60 if outcome == 'DEFAULTED' else 0)
    }


def import_dataset(data: List[Dict[str, Any]], mappings: Dict[str, str]) -> Tuple[int, int]:
    """
    Import a dataset into historical cases.
    Returns (imported_count, skipped_count)
    """
    imported_cases = []
    skipped = 0
    
    for idx, row in enumerate(data):
        try:
            case = convert_row_to_case(row, mappings, idx)
            imported_cases.append(case)
        except Exception as e:
            skipped += 1
            continue
    
    set_historical_cases(imported_cases)
    
    return len(imported_cases), skipped
