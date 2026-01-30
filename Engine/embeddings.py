"""
embeddings.py
-------------
Embedding generation module for loan applications.

This module handles the transformation of loan application data into vectors.
Separated from vector_store.py to maintain clean architecture.
"""

import numpy as np
from typing import Dict, List, Any


def encode_grade(grade: str) -> float:
    """
    Convert credit grade (A-G) to normalized score (0-1)
    
    Args:
        grade: Credit grade (A, B, C, D, E, F, G)
    
    Returns:
        Score between 0 and 1 (A=1.0, G=0.1)
    """
    if not grade:
        return 0.5
    
    grades = {
        "A": 1.0,
        "B": 0.85,
        "C": 0.70,
        "D": 0.55,
        "E": 0.40,
        "F": 0.25,
        "G": 0.10
    }
    return grades.get(grade.strip(), 0.5)


def create_application_vector(application: Dict[str, Any], vector_size: int = 50) -> List[float]:
    """
    Create a normalized vector from a loan application
    
    Uses:
    - Logarithmic normalization for amounts
    - Min-max normalization for ratios
    - One-hot encoding for categories
    
    Args:
        application: Dict containing application features
        vector_size: Target vector dimension (default: 50)
    
    Returns:
        List of normalized floats between 0 and 1
    """
    
    # Continuous features (normalized)
    vector = [
        # Amounts (log-normalized)
        np.log1p(application.get("requested_amount") or 0) / 15,
        np.log1p(application.get("annual_income_snapshot") or 0) / 15,
        
        # Financial ratios (capped at 1.0)
        min((application.get("dti_snapshot") or 0) / 100, 1),
        min((application.get("payment_to_income_ratio") or 0), 1),
        min((application.get("loan_to_income_ratio") or 0), 1),
        min((application.get("revolving_utilization_snapshot") or 0) / 100, 1),
        
        # Credit score
        (application.get("fico_snapshot") or 650) / 850,
        
        # Client history
        min((application.get("credit_history_length_snapshot") or 0) / 50, 1),
        min((application.get("nb_previous_loans") or 0) / 10, 1),
        min((application.get("open_accounts") or 0) / 30, 1),
        min((application.get("total_accounts") or 0) / 50, 1),
        
        # Negative signals
        min((application.get("delinquencies_2y") or 0) / 10, 1),
        min((application.get("inquiries_6m") or 0) / 10, 1),
        min((application.get("public_records") or 0) / 5, 1),
        
        # Categorical features (one-hot encoding)
        # Term
        1.0 if application.get("term") == " 36 months" else 0.0,
        1.0 if application.get("term") == " 60 months" else 0.0,
        
        # Grade
        encode_grade(application.get("grade")),
        
        # Purpose (top 5)
        1.0 if application.get("loan_purpose") == "debt_consolidation" else 0.0,
        1.0 if application.get("loan_purpose") == "credit_card" else 0.0,
        1.0 if application.get("loan_purpose") == "home_improvement" else 0.0,
        1.0 if application.get("loan_purpose") == "other" else 0.0,
        1.0 if application.get("loan_purpose") == "major_purchase" else 0.0,
    ]
    
    # Pad to vector_size
    while len(vector) < vector_size:
        vector.append(0.0)
    
    return vector[:vector_size]