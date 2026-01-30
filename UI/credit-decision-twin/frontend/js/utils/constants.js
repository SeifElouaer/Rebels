// Constants for CreditTwin application

const API_BASE_URL = 'http://localhost:8000';

const EMPLOYMENT_TYPES = ['full-time', 'part-time', 'self-employed', 'contractor', 'retired'];
const SECTORS = ['technology', 'healthcare', 'finance', 'retail', 'manufacturing', 'education', 'government', 'other'];
const PURPOSES = ['home', 'auto', 'personal', 'business', 'education', 'debt-consolidation'];
const REGIONS = ['northeast', 'southeast', 'midwest', 'southwest', 'west'];

const VECTOR_DIMENSIONS = 768;

// Auto-mapping patterns for CSV/Excel column detection
const AUTO_MAP_PATTERNS = {
    'age': ['age', 'borrower_age', 'applicant_age'],
    'credit_score': ['credit_score', 'creditscore', 'fico', 'score', 'credit'],
    'income': ['income', 'annual_income', 'yearly_income', 'salary'],
    'loan_amount': ['loan_amount', 'loanamount', 'amount', 'principal', 'loan_amnt'],
    'debt': ['debt', 'total_debt', 'liabilities', 'outstanding_debt'],
    'assets': ['assets', 'total_assets', 'net_worth'],
    'tenure': ['tenure', 'term', 'loan_term', 'months', 'duration'],
    'employment': ['employment', 'employment_type', 'emp_type', 'job_type'],
    'sector': ['sector', 'industry', 'job_sector', 'business_sector'],
    'purpose': ['purpose', 'loan_purpose', 'reason'],
    'region': ['region', 'state', 'location', 'area', 'addr_state'],
    'outcome': ['outcome', 'status', 'loan_status', 'result', 'default', 'defaulted'],
    'days_late': ['days_late', 'dayslate', 'late_days', 'delinquent_days']
};

// Default applicant values
const DEFAULT_APPLICANT = {
    age: 35,
    credit_score: 720,
    income: 75000,
    debt: 15000,
    assets: 120000,
    loan_amount: 25000,
    tenure: 36,
    employment: 'full-time',
    sector: 'technology',
    purpose: 'home',
    region: 'northeast'
};

// Auto-map columns based on header names
function autoMapColumns(headers) {
    const mappings = {};
    
    Object.keys(AUTO_MAP_PATTERNS).forEach(field => {
        const patterns = AUTO_MAP_PATTERNS[field];
        for (const pattern of patterns) {
            const match = headers.find(h => h.toLowerCase().includes(pattern.toLowerCase()));
            if (match) {
                mappings[field] = match;
                break;
            }
        }
    });
    
    return mappings;
}
