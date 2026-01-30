# CreditTwin: Financial Twin Decision Engine 🧠

CreditTwin is a premium financial intelligence platform that evaluates credit applications by finding "financial twins" in historical data (300,000+ records). It moves beyond basic approval and rejection, providing predictive guidance for every applicant.

## ✨ Advanced Intelligence Features

- **Path to Success (Roadmap)**: Provides rejected applicants with a personalized improvement roadmap (Target FICO/DTI) based on "Comeback Twins" who succeeded after initial rejection.
- **Fraud & Anomaly Detection**: Real-time identification of "Identity Anomalies" using vector similarity patterns to flag high-risk applications.
- **Smart Product Up-Selling**: Suggests safer loan amount alternatives if the initial request is too risky, keeping customers in the ecosystem.
- **Smart Nudges**: Predicts a client's "Next Best Action" (e.g., Home Improvement loans) based on the future behavior of their financial twins.
- **Automatic DTI Calculation**: Simplifies user input by automatically calculating Debt-to-Income ratios from monthly debt.

## 🧪 Interactive Test Scenarios

Try these cases in the **New Application** form to see the intelligence engine in action:

1.  **The "Golden" Approved**: `10k Loan | 90k Income | 790 FICO` → **Result**: Approved + Smart Nudge pro-tip.
2.  **The "Comeback" Roadmap**: `10k Loan | 30k Income | 520 FICO` → **Result**: Rejected + Personalized Path to Success.
3.  **The "Up-Sell" Alternative**: `45k Loan | 55k Income | 710 FICO` → **Result**: Rejected + Suggested safer loan limit card.
4.  **The "Manual Review" Zone**: `15k Loan | 50k Income | 680 FICO` → **Result**: Manual Underwriting (Gray zone analysis).
5.  **The "Fraud" Anomaly**: `2k Loan | 150k Income | 840 FICO` → **Result**: Identity Anomaly Detected (High-risk alert).

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Docker (for Qdrant Vector Database)

### 2. Start Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Setup and Run (Auto)
Run the automated batch file to install dependencies, process data, and start the engine:
`run_CreditTwin.bat`

### 4. Manual Setup
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Setup Database**: `python Engine/data_loader.py`
3. **Build Vector Store**: `python Engine/buildvector_store.py`
4. **Start API**: `python Engine/app.py`

## 🎨 UI/UX Highlights
- **Premium Dark Mode Dashboard**: Glassmorphism design with real-time success rate tracking.
- **Engine Interpretation**: Human-friendly explanations for every decision.
- **Interactive Twin Analysis**: Visual comparison with the top 10 most similar historical cases.

## 🛠️ Project Structure
- `Engine/`: Decision core, Vector search, and API layer.
- `data/`: Source CSV data (Accepted & Rejected loans).
- `db/`: SQLite database for structured persistence.

## ⚠️ Data Note
This project utilizes a balanced dataset of 300,000 applications (150k Accepted / 150k Rejected) to ensure fair and accurate similarity matching.
