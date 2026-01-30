"""
data_loader.py
--------------
Enhanced version with Advanced Insights support:
- Identifies "Comeback Twins" (Rejection -> Success)
- Flags "Similarity Anomalies" (Fraud Detection)
- Prepares data for Product Up-Selling & Smart Nudges
"""

import pandas as pd
import sqlite3
import hashlib
import json
import os
import sys

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# Trouve le dossier racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "credit.db")
ACCEPTED_CSV = os.path.join(BASE_DIR, "data", "accepted_2007_to_2018Q4.csv")
REJECTED_CSV = os.path.join(BASE_DIR, "data", "rejected_lite.csv")


def categorize_outcome(status):
    """
    Simplifie les statuts de prêt en catégories utilisables
    """
    if pd.isna(status):
        return "unknown"
    
    status = str(status).lower()
    
    if status in ["fully paid", "current"]:
        return "success"
    elif status in ["charged off", "default"]:
        return "default"
    elif status in ["late (31-120 days)", "late (16-30 days)"]:
        return "late_payments"
    else:
        return "other"


def make_applicant_id(row):
    """
    Génère un ID unique anonymisé pour chaque client, compatible accepted/rejected
    """
    state = row.get('addr_state') or row.get('State') or 'XX'
    emp = row.get('emp_length') or row.get('Employment Length') or 'Unknown'
    fico = row.get('fico_range_low') or row.get('Risk_Score') or 600
    
    raw = f"{state}|{emp}|{fico}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def create_sql_database():
    """
    Crée la base de données SQLite en intégrant les données acceptées et refusées.
    Maintenant identifie également les patterns avancés (Comebacks, Fraude).
    """
    
    # ---------------------------------------------------------
    # PART 1: Load and Prepare Accepted Data
    # ---------------------------------------------------------
    print("📥 Loading accepted CSV data...")
    if not os.path.exists(ACCEPTED_CSV):
        raise FileNotFoundError(f"CSV file not found: {ACCEPTED_CSV}")
    
    df_acc = pd.read_csv(ACCEPTED_CSV, low_memory=False, nrows=500)
    print(f"   Loaded {len(df_acc)} accepted loans (LITE MODE)")
    
    print("📅 Parsing dates and calculating history...")
    df_acc["issue_d"] = pd.to_datetime(df_acc["issue_d"], format="%b-%Y", errors="coerce")
    df_acc["earliest_cr_line"] = pd.to_datetime(df_acc["earliest_cr_line"], format="%b-%Y", errors="coerce")
    
    df_acc["credit_history_length_years"] = (
        (df_acc["issue_d"] - df_acc["earliest_cr_line"]).dt.days / 365.25
    )
    
    # Generate IDs
    df_acc["applicant_id"] = df_acc.apply(make_applicant_id, axis=1)
    df_acc["application_id"] = df_acc.apply(
        lambda row: f"APP-{row['issue_d'].strftime('%Y%m%d') if pd.notna(row['issue_d']) else 'UNKNOWN'}-{row.name}",
        axis=1
    )
    
    # Sort for sequence analysis
    df_acc = df_acc.sort_values(["applicant_id", "issue_d"])
    df_acc["nb_previous_loans"] = df_acc.groupby("applicant_id").cumcount()
    
    # ---------------------------------------------------------
    # PART 2: Load and Prepare Rejected Data
    # ---------------------------------------------------------
    print("📤 Loading rejected CSV data...")
    if os.path.exists(REJECTED_CSV):
        df_rej = pd.read_csv(REJECTED_CSV, low_memory=False, nrows=500)
        print(f"   Loaded {len(df_rej)} rejected applications (LITE MODE)")
        
        # Parse dates
        df_rej["Application Date"] = pd.to_datetime(df_rej["Application Date"], errors="coerce")
        
        # Clean DTI (remove %)
        def clean_dti(dti):
            if pd.isna(dti): return 0.0
            if isinstance(dti, str):
                return float(dti.replace('%', ''))
            return float(dti)
        
        df_rej["dti_clean"] = df_rej["Debt-To-Income Ratio"].apply(clean_dti)
        
        # Generate IDs
        df_rej["applicant_id"] = df_rej.apply(make_applicant_id, axis=1)
        df_rej["application_id"] = df_rej.apply(
            lambda row: f"REJ-{row['Application Date'].strftime('%Y%m%d') if pd.notna(row['Application Date']) else 'UNKNOWN'}-{row.name}",
            axis=1
        )
        
        # Sort for sequence analysis
        df_rej = df_rej.sort_values(["applicant_id", "Application Date"])
    else:
        print("   ⚠️  Rejected CSV not found, skipping...")
        df_rej = pd.DataFrame()

    # ---------------------------------------------------------
    # PART 3: ADVANCED INSIGHTS IDENTIFICATION
    # ---------------------------------------------------------
    print("🧠 Identifying Advanced Insights (Comebacks & Fraud Patterns)...")
    
    # 1. Identity Anomaly (Fraud Pattern): Detect if same ID appears with wildly different income/FICO
    # (Simulated for this hackathon: Find IDs with high variance in requested amount)
    fraud_ids = set()
    if not df_acc.empty:
        # Just an example heuristic for anomaly detection
        std_amounts = df_acc.groupby('applicant_id')['loan_amnt'].std()
        fraud_ids = set(std_amounts[std_amounts > 20000].index)
        print(f"   - Identified {len(fraud_ids)} potential identity anomalies")

    # 2. Comeback Twins: Clients who had a rejection before an approval
    comeback_ids = set()
    if not df_rej.empty and not df_acc.empty:
        rej_ids = set(df_rej["applicant_id"].unique())
        acc_ids = set(df_acc["applicant_id"].unique())
        comeback_ids = rej_ids.intersection(acc_ids)
        print(f"   - Identified {len(comeback_ids)} 'Comeback' success stories")

    # ---------------------------------------------------------
    # PART 3.1: Final Table Preparation
    # ---------------------------------------------------------

    # 1. Prepare Applications from accepted
    print("📝 Preparing applications from accepted loans...")
    df_apps_acc = pd.DataFrame({
        "application_id": df_acc["application_id"],
        "applicant_id": df_acc["applicant_id"],
        "application_date": df_acc["issue_d"].astype(str),
        "requested_amount": df_acc["loan_amnt"],
        "loan_purpose": df_acc["purpose"],
        "term": df_acc["term"],
        "grade": df_acc["grade"],
        "sub_grade": df_acc["sub_grade"],
        "annual_income_snapshot": df_acc["annual_inc"],
        "dti_snapshot": df_acc["dti"],
        "fico_snapshot": (df_acc["fico_range_low"] + df_acc["fico_range_high"]) / 2,
        "credit_history_length_snapshot": df_acc["credit_history_length_years"],
        "revolving_balance_snapshot": df_acc["revol_bal"],
        "revolving_utilization_snapshot": df_acc["revol_util"],
        "installment": df_acc["installment"],
        "nb_previous_loans": df_acc["nb_previous_loans"],
        "open_accounts": df_acc["open_acc"],
        "total_accounts": df_acc["total_acc"],
        "delinquencies_2y": df_acc["delinq_2yrs"],
        "inquiries_6m": df_acc["inq_last_6mths"],
        "public_records": df_acc["pub_rec"],
        "payment_to_income_ratio": (df_acc["installment"] / (df_acc["annual_inc"] / 12)).round(4),
        "loan_to_income_ratio": (df_acc["loan_amnt"] / df_acc["annual_inc"]).round(4),
        "loan_status": df_acc["loan_status"],
        "was_approved": 1,
        "outcome_category": df_acc["loan_status"].apply(categorize_outcome),
        "total_payments": df_acc["total_pymnt"],
        "total_received": df_acc["total_rec_prncp"],
        "recoveries": df_acc["recoveries"],
        # Advanced Tags
        "is_fraud_suspect": df_acc["applicant_id"].isin(fraud_ids).astype(int),
        "is_comeback_story": df_acc["applicant_id"].isin(comeback_ids).astype(int)
    })

    # 2. Prepare Applications from rejected
    df_apps_rej = pd.DataFrame()
    if not df_rej.empty:
        print("📝 Preparing applications from rejected loans...")
        df_apps_rej = pd.DataFrame({
            "application_id": df_rej["application_id"],
            "applicant_id": df_rej["applicant_id"],
            "application_date": df_rej["Application Date"].astype(str),
            "requested_amount": df_rej["Amount Requested"],
            "loan_purpose": df_rej["Loan Title"],
            "term": None, "grade": None, "sub_grade": None,
            "annual_income_snapshot": None,
            "dti_snapshot": df_rej["dti_clean"],
            "fico_snapshot": df_rej["Risk_Score"],
            "credit_history_length_snapshot": None, "revolving_balance_snapshot": None, "revolving_utilization_snapshot": None, "installment": None,
            "nb_previous_loans": 0, "open_accounts": None, "total_accounts": None, "delinquencies_2y": None, "inquiries_6m": None, "public_records": None,
            "payment_to_income_ratio": None, "loan_to_income_ratio": None,
            "loan_status": "Rejected",
            "was_approved": 0,
            "outcome_category": "rejected",
            "total_payments": 0, "total_received": 0, "recoveries": 0,
            # Advanced Tags
            "is_fraud_suspect": df_rej["applicant_id"].isin(fraud_ids).astype(int),
            "is_comeback_story": 0 # Rejected isn't a comeback yet
        })

    df_applications_final = pd.concat([df_apps_acc, df_apps_rej])

    # 3. Final Clients table
    print("👥 Finalizing clients table...")
    df_c_acc = pd.DataFrame({
        "applicant_id": df_acc["applicant_id"],
        "state": df_acc["addr_state"],
        "employment_length": df_acc["emp_length"],
        "fico_score": (df_acc["fico_range_low"] + df_acc["fico_range_high"]) / 2,
        "earliest_credit_line": df_acc["earliest_cr_line"].astype(str),
        "first_application_date": df_acc["issue_d"].astype(str),
    })
    
    df_c_rej = pd.DataFrame()
    if not df_rej.empty:
        df_c_rej = pd.DataFrame({
            "applicant_id": df_rej["applicant_id"],
            "state": df_rej["State"],
            "employment_length": df_rej["Employment Length"],
            "fico_score": df_rej["Risk_Score"],
            "earliest_credit_line": None,
            "first_application_date": df_rej["Application Date"].astype(str),
        })
    
    df_clients_final = pd.concat([df_c_acc, df_c_rej]).drop_duplicates(subset=["applicant_id"])

    # ---------------------------------------------------------
    # PART 4: Save to SQLite
    # ---------------------------------------------------------
    print("💾 Saving to SQLite database...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS applications")
    cursor.execute("DROP TABLE IF EXISTS clients")
    
    cursor.execute("""
    CREATE TABLE clients (
        applicant_id TEXT PRIMARY KEY,
        state TEXT,
        employment_length TEXT,
        fico_score REAL,
        earliest_credit_line TEXT,
        first_application_date TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE applications (
        application_id TEXT PRIMARY KEY,
        applicant_id TEXT,
        application_date TEXT,
        requested_amount REAL,
        loan_purpose TEXT,
        term TEXT,
        grade TEXT,
        sub_grade TEXT,
        annual_income_snapshot REAL,
        dti_snapshot REAL,
        fico_snapshot REAL,
        credit_history_length_snapshot REAL,
        revolving_balance_snapshot REAL,
        revolving_utilization_snapshot REAL,
        installment REAL,
        nb_previous_loans INTEGER,
        open_accounts INTEGER,
        total_accounts INTEGER,
        delinquencies_2y INTEGER,
        inquiries_6m INTEGER,
        public_records INTEGER,
        payment_to_income_ratio REAL,
        loan_to_income_ratio REAL,
        loan_status TEXT,
        was_approved BOOLEAN,
        outcome_category TEXT,
        total_payments REAL,
        total_received REAL,
        recoveries REAL,
        is_fraud_suspect INTEGER,
        is_comeback_story INTEGER,
        FOREIGN KEY (applicant_id) REFERENCES clients(applicant_id)
    )
    """)
    
    df_clients_final.to_sql("clients", conn, if_exists="append", index=False)
    df_applications_final.to_sql("applications", conn, if_exists="append", index=False)
    
    cursor.execute("CREATE INDEX idx_applicant ON applications(applicant_id)")
    cursor.execute("CREATE INDEX idx_outcome ON applications(outcome_category)")
    cursor.execute("CREATE INDEX idx_date ON applications(application_date)")
    cursor.execute("CREATE INDEX idx_fraud ON applications(is_fraud_suspect)")
    cursor.execute("CREATE INDEX idx_comeback ON applications(is_comeback_story)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully")
    print(f"   - {len(df_clients_final)} unique clients")
    print(f"   - {len(df_applications_final)} total applications")
    print(f"   - Location: {DB_PATH}")


def export_applications_to_json():
    """
    Exporte les demandes avec résultat connu vers JSON pour Qdrant
    """
    print("📤 Exporting applications with known outcomes...")
    
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    
    # We export everything with known outcomes + rejected
    query = "SELECT * FROM applications WHERE outcome_category IN ('success', 'default', 'late_payments', 'rejected')"
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"   Found {len(df)} applications for vectorization")
    
    applications = df.to_dict('records')
    for app in applications:
        for key, value in app.items():
            if pd.isna(value):
                app[key] = None
    
    json_path = os.path.join(BASE_DIR, "Engine", "loan_requests.json")
    with open(json_path, "w") as f:
        json.dump(applications, f, indent=2)
    
    print(f"✅ Exported to: loan_requests.json")
    return applications


def verify_database():
    """
    Vérifie l'intégrité de la base de données
    """
    print("\n🔍 Verifying database integrity...")
    if not os.path.exists(DB_PATH):
        print("   ❌ Database file not found")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        print(f"   ✓ Clients: {client_count:,} records")
        
        cursor.execute("SELECT is_comeback_story, COUNT(*) FROM applications GROUP BY is_comeback_story")
        comebacks = dict(cursor.fetchall())
        print(f"   ✓ Comeback Stories: {comebacks.get(1, 0):,} records")
        
        cursor.execute("SELECT is_fraud_suspect, COUNT(*) FROM applications GROUP BY is_fraud_suspect")
        frauds = dict(cursor.fetchall())
        print(f"   ✓ Fraud Suspects: {frauds.get(1, 0):,}")

        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        conn.close()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("CreditTwin Data Loader (Advanced)".center(70))
    print("=" * 70)
    
    try:
        create_sql_database()
        export_applications_to_json()
        verify_database()
        
        print("=" * 70)
        print("✅ All operations completed successfully".center(70))
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise