"""
CreditTwin API - FastAPI Backend
"""
import io
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd

from models import (
    CreditApplication,
    ColumnMapping,
    CreditDecisionResponse,
    DatabaseStats,
    UploadResponse,
    DataSourceInfo,
    HistoricalCase
)
from services import (
    process_credit_application,
    get_database_stats,
    get_case_count,
    get_sample_cases,
    get_historical_cases,
    clear_historical_cases,
    import_dataset,
    PURPOSES
)

# Initialize FastAPI app
app = FastAPI(
    title="CreditTwin API",
    description="Multimodal Similarity-Driven Credit Risk & Anomaly Detection",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store uploaded file info
upload_info = {
    "headers": [],
    "data": [],
    "filename": ""
}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "CreditTwin API is running"}


@app.get("/api/status")
async def get_status():
    """Get API and database status"""
    return {
        "api_status": "connected",
        "qdrant_status": "connected",  # Placeholder
        "case_count": get_case_count()
    }


@app.get("/api/data-source", response_model=DataSourceInfo)
async def get_data_source():
    """Get current data source information"""
    count = get_case_count()
    if count == 0:
        return DataSourceInfo(
            type="none",
            count=0,
            label="No data loaded"
        )
    return DataSourceInfo(
        type="custom",
        count=count,
        label=f"Custom Data ({count:,} cases)"
    )


@app.post("/api/process-application", response_model=CreditDecisionResponse)
async def process_application(application: CreditApplication):
    """
    Process a new credit application and return decision with explanations.
    """
    if get_case_count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No historical data loaded. Please upload a dataset first."
        )
    
    result = process_credit_application(application)
    return result


@app.get("/api/stats", response_model=DatabaseStats)
async def get_stats():
    """Get database statistics"""
    return get_database_stats()


@app.get("/api/sample-cases", response_model=List[HistoricalCase])
async def get_sample(count: int = 20):
    """Get a random sample of historical cases"""
    cases = get_sample_cases(count)
    return [
        HistoricalCase(
            id=c.get('id', 'UNKNOWN'),
            age=c.get('age', 0),
            credit_score=c.get('credit_score', 0),
            income=c.get('income', 0),
            loan_amount=c.get('loan_amount', 0),
            purpose=c.get('purpose', 'unknown'),
            decision=c.get('decision', 'UNKNOWN'),
            outcome=c.get('outcome', 'UNKNOWN'),
            days_late=c.get('days_late', 0)
        )
        for c in cases
    ]


@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an Excel or CSV file for preview.
    Returns headers and sample data for column mapping.
    """
    filename = file.filename.lower()
    
    if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid Excel (.xlsx, .xls) or CSV (.csv) file."
        )
    
    try:
        contents = await file.read()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Store for later import
        upload_info["headers"] = df.columns.tolist()
        upload_info["data"] = df.to_dict('records')
        upload_info["filename"] = file.filename
        
        # Return preview
        preview_data = df.head(5).to_dict('records')
        
        return {
            "success": True,
            "filename": file.filename,
            "headers": upload_info["headers"],
            "row_count": len(df),
            "preview": preview_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error parsing file: {str(e)}"
        )


@app.post("/api/import-dataset", response_model=UploadResponse)
async def import_uploaded_dataset(mappings: ColumnMapping):
    """
    Import the uploaded dataset using the provided column mappings.
    """
    if not upload_info["data"]:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a file first."
        )
    
    # Validate required mappings
    if not all([mappings.age, mappings.credit_score, mappings.income, mappings.loan_amount, mappings.outcome]):
        raise HTTPException(
            status_code=400,
            detail="Please map all required fields: Age, Credit Score, Income, Loan Amount, and Outcome."
        )
    
    # Convert mappings to dict
    mapping_dict = {
        'age': mappings.age,
        'credit_score': mappings.credit_score,
        'income': mappings.income,
        'loan_amount': mappings.loan_amount,
        'outcome': mappings.outcome,
        'debt': mappings.debt,
        'assets': mappings.assets,
        'tenure': mappings.tenure,
        'employment': mappings.employment,
        'sector': mappings.sector,
        'purpose': mappings.purpose,
        'region': mappings.region,
        'days_late': mappings.days_late,
    }
    
    # Import the data
    imported_count, skipped_count = import_dataset(upload_info["data"], mapping_dict)
    
    if imported_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Could not import any valid rows. Please check your column mappings."
        )
    
    return UploadResponse(
        success=True,
        message=f"Successfully imported {imported_count:,} cases to Qdrant vector database.",
        imported_count=imported_count,
        skipped_rows=skipped_count,
        headers=upload_info["headers"]
    )


@app.post("/api/clear-data")
async def clear_data():
    """Clear all historical data"""
    clear_historical_cases()
    upload_info["headers"] = []
    upload_info["data"] = []
    upload_info["filename"] = ""
    
    return {"success": True, "message": "All data cleared."}


@app.post("/api/reset-data")
async def reset_data():
    """Reset to synthetic data"""
    from services import set_historical_cases, generate_synthetic_data
    
    cases = generate_synthetic_data(1000)
    set_historical_cases(cases)
    
    upload_info["headers"] = []
    upload_info["data"] = []
    upload_info["filename"] = ""
    
    return {
        "success": True, 
        "message": f"Reset to synthetic data with {len(cases):,} cases.",
        "count": len(cases)
    }


@app.get("/api/export-data")
async def export_data():
    """Export current dataset as CSV"""
    cases = get_historical_cases()
    
    if not cases:
        raise HTTPException(
            status_code=400,
            detail="No data to export."
        )
    
    df = pd.DataFrame(cases)
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=credit_twin_export.csv"}
    )


@app.get("/api/download-template")
async def download_template():
    """Download a CSV template with expected columns"""
    template_data = {
        'age': [35, 42, 28],
        'credit_score': [720, 650, 780],
        'income': [75000, 55000, 95000],
        'loan_amount': [25000, 15000, 40000],
        'debt': [15000, 25000, 10000],
        'assets': [120000, 80000, 200000],
        'tenure': [36, 24, 48],
        'employment': ['full-time', 'self-employed', 'full-time'],
        'sector': ['technology', 'retail', 'healthcare'],
        'purpose': ['home', 'personal', 'auto'],
        'region': ['northeast', 'west', 'southeast'],
        'outcome': ['REPAID', 'DEFAULTED', 'REPAID'],
        'days_late': [0, 45, 0]
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=credit_twin_template.csv"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
