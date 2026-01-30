# CreditTwin - Multimodal Credit Decision Memory

A hackathon project demonstrating similarity-driven credit risk assessment and anomaly detection using vector search.

## 🏗️ Project Structure

```
credit-twin/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # API endpoints
│   ├── models.py              # Pydantic models
│   ├── services.py            # Business logic (placeholder for your engine)
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React.js frontend
│   ├── index.html             # Main HTML entry point
│   ├── css/
│   │   └── styles.css         # Global styles
│   └── js/
│       ├── utils/
│       │   ├── constants.js   # App constants
│       │   └── api.js         # API client functions
│       ├── context/
│       │   └── AppContext.js  # React Context for state
│       ├── components/
│       │   ├── Header.js
│       │   ├── ApplicationTab.js
│       │   ├── ResultsPanel.js
│       │   ├── DatabaseTab.js
│       │   └── ArchitectureTab.js
│       └── App.js             # Main App component
│
└── README.md
```

## 🚀 Getting Started

### 1. Start the Python Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Serve the Frontend

You can use any static file server. For example:

```bash
cd frontend

# Using Python
python -m http.server 3000

# Using Node.js (if installed)
npx serve -p 3000
```

Open `http://localhost:3000` in your browser.

## 📤 Upload Your Dataset

1. Go to the **"Historical Database"** tab
2. Drag & drop your Excel file (.xlsx) or click to browse
3. Map your columns to the required fields:
   - **Required**: Age, Credit Score, Income, Loan Amount, Outcome
   - **Optional**: Debt, Assets, Tenure, Employment, Sector, Purpose, Region, Days Late
4. Click **"Import Dataset to Qdrant"**

## 🔧 Adding Your Credit Decision Engine

The backend has placeholder functions in `backend/services.py` that you can replace with your actual implementation:

### Key functions to implement:

1. **`create_feature_vector(applicant)`** - Convert applicant data to embedding vector
2. **`find_financial_twins(applicant, k)`** - Query Qdrant for similar cases
3. **`calculate_anomaly_score(twins)`** - Compute anomaly score from similarity distribution
4. **`detect_anomaly_flags(applicant)`** - Detect specific anomaly patterns
5. **`make_decision(twins, anomaly_score, applicant)`** - Make credit decision

### Example Qdrant integration:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Initialize client
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="credit_cases",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# Search for twins
results = client.search(
    collection_name="credit_cases",
    query_vector=applicant_embedding,
    limit=50
)
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Check API and Qdrant status |
| `/api/data-source` | GET | Get current data source info |
| `/api/process-application` | POST | Process a credit application |
| `/api/stats` | GET | Get database statistics |
| `/api/sample-cases` | GET | Get sample historical cases |
| `/api/upload-file` | POST | Upload Excel/CSV file |
| `/api/import-dataset` | POST | Import uploaded data with mappings |
| `/api/clear-data` | POST | Clear all data |
| `/api/export-data` | GET | Export data as CSV |
| `/api/download-template` | GET | Download CSV template |

## 🎯 Features

- **Financial Twin Matching**: Find similar historical borrowers using vector similarity
- **Anomaly Detection**: Identify unusual application patterns
- **Explainable Decisions**: Full audit trail with case references
- **Excel Upload**: Import your 150,000 historical credit cases
- **Interactive Charts**: Visualize cohort outcomes and payment behavior

## 📝 License

MIT License - Hackathon 2024
