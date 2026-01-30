"""
Pydantic models for CreditTwin API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    SELF_EMPLOYED = "self-employed"
    CONTRACTOR = "contractor"
    RETIRED = "retired"


class Sector(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    GOVERNMENT = "government"
    OTHER = "other"


class LoanPurpose(str, Enum):
    HOME = "home"
    AUTO = "auto"
    PERSONAL = "personal"
    BUSINESS = "business"
    EDUCATION = "education"
    DEBT_CONSOLIDATION = "debt-consolidation"


class Region(str, Enum):
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    MIDWEST = "midwest"
    SOUTHWEST = "southwest"
    WEST = "west"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    DECLINE = "DECLINE"


class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Outcome(str, Enum):
    REPAID = "REPAID"
    DEFAULTED = "DEFAULTED"


# Request Models
class CreditApplication(BaseModel):
    """New credit application input"""
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    income: float = Field(..., gt=0, description="Annual income")
    debt: float = Field(..., ge=0, description="Total debt")
    assets: float = Field(..., ge=0, description="Total assets")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    tenure: int = Field(..., ge=6, le=360, description="Loan term in months")
    employment: EmploymentType = Field(..., description="Employment type")
    sector: Sector = Field(..., description="Industry sector")
    purpose: LoanPurpose = Field(..., description="Loan purpose")
    region: Region = Field(..., description="Geographic region")


class ColumnMapping(BaseModel):
    """Column mapping for dataset import"""
    age: str
    credit_score: str
    income: str
    loan_amount: str
    outcome: str
    debt: Optional[str] = None
    assets: Optional[str] = None
    tenure: Optional[str] = None
    employment: Optional[str] = None
    sector: Optional[str] = None
    purpose: Optional[str] = None
    region: Optional[str] = None
    days_late: Optional[str] = None


# Response Models
class FinancialTwin(BaseModel):
    """A similar historical case"""
    id: str
    borrower_id: str
    age: int
    credit_score: int
    income: float
    debt: float
    assets: float
    loan_amount: float
    tenure: int
    employment: str
    sector: str
    purpose: str
    region: str
    decision: str
    outcome: str
    days_late: int
    similarity: float


class AnomalyFlag(BaseModel):
    """Anomaly detection flag"""
    type: str  # 'warning', 'alert', 'info'
    text: str


class DecisionResult(BaseModel):
    """Credit decision output"""
    decision: Decision
    confidence: float = Field(..., ge=0, le=1)
    risk_tier: RiskTier
    reason: str
    default_rate: float
    avg_days_late: float
    repaid_count: int
    default_count: int


class CreditDecisionResponse(BaseModel):
    """Full response for credit application"""
    twins: List[FinancialTwin]
    anomaly_score: float
    flags: List[AnomalyFlag]
    decision: DecisionResult


class DatabaseStats(BaseModel):
    """Database statistics"""
    total: int
    repaid: int
    defaulted: int
    purpose_counts: Dict[str, int]


class UploadResponse(BaseModel):
    """Response after uploading dataset"""
    success: bool
    message: str
    imported_count: int
    skipped_rows: int
    headers: List[str]


class DataSourceInfo(BaseModel):
    """Current data source information"""
    type: str  # 'none', 'custom'
    count: int
    label: str


class HistoricalCase(BaseModel):
    """Historical credit case for table display"""
    id: str
    age: int
    credit_score: int
    income: float
    loan_amount: float
    purpose: str
    decision: str
    outcome: str
    days_late: int
