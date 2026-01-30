"""
llm_explanation.py
------------------
Module for generating human-friendly credit decision explanations using Google Gemini.
"""

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in environment. LLM explanations will be disabled.")

def get_llm_explanation(decision_data, applicant_info):
    """
    Generate a human-friendly explanation for a credit decision using Google Gemini.
    
    Args:
        decision_data: The decision dictionary (decision, confidence, reason, analysis, etc.)
        applicant_info: The original application data
        
    Returns:
        A string containing the AI-generated explanation or None if LLM is unavailable.
    """
    if not GOOGLE_API_KEY:
        return None

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Prepare context for the prompt
        prompt = f"""
        You are a helpful and empathetic financial advisor at 'CreditTwin', a premium financial intelligence platform.
        Your task is to explain a credit decision to a customer based on 'Financial Twin Matching' (comparing them to similar historical cases).

        DECISION DETAILS:
        - Decision: {decision_data.get('decision')}
        - Confidence: {decision_data.get('confidence', 0)*100:.1f}%
        - Core Reason: {decision_data.get('reason')}
        - Success Rate among similar profiles: {decision_data.get('analysis', {}).get('success_rate', 0)*100:.1f}%
        
        APPLICANT PROFILE:
        - Requested Amount: ${applicant_info.get('requested_amount', 0):,}
        - FICO Score: {applicant_info.get('fico_snapshot')}
        - Debt-to-Income (DTI): {applicant_info.get('dti_snapshot', 0):.1f}%
        - Monthly Income: ${applicant_info.get('annual_income_snapshot', 0)/12:,.0f}

        GUIDELINES:
        1. Be transparent but supportive.
        2. Use the 'Financial Twin' concept: explain that we found thousands of similar historical profiles and their outcomes influenced this decision.
        3. If APPROVED: Be celebratory and mention why they are a strong match.
        4. If REJECTED: Be professional, empathetic, and briefly mention what they could improve (DTI, FICO) based on the data.
        5. Keep it concise (3-4 sentences).
        6. Do not use technical jargon like 'vector embeddings' or 'Qdrant'. Use terms like 'financial profile matching'.

        Write the explanation for the customer:
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Error generating LLM explanation: {e}")
        return None
