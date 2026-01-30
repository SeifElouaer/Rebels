import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api_status():
    print("Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        response.raise_for_status()
        data = response.json()
        print(f"Status: {data}")
        assert data["api_status"] == "connected"
        assert "case_count" in data
        print("PASS: API status check")
    except Exception as e:
        print(f"FAIL: API status check - {str(e)}")

def test_reset_data():
    print("\nTesting Reset Data...")
    try:
        response = requests.post(f"{BASE_URL}/reset-data")
        response.raise_for_status()
        data = response.json()
        print(f"Reset Response: {data}")
        assert data["success"] == True
        assert data["count"] > 0
        print("PASS: Reset data")
    except Exception as e:
        print(f"FAIL: Reset data - {str(e)}")

def test_process_application():
    print("\nTesting Process Application...")
    applicant = {
        "age": 35,
        "credit_score": 720,
        "income": 75000,
        "debt": 15000,
        "assets": 120000,
        "loan_amount": 25000,
        "tenure": 36,
        "employment": "full-time",
        "sector": "technology",
        "purpose": "home",
        "region": "northeast",
        "delinquencies": 0,
        "utilization": 30,
        "historyLength": 8
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-application", json=applicant)
        response.raise_for_status()
        data = response.json()
        
        print(f"Decision: {data['decision']['decision']}")
        print(f"Confidence: {data['decision']['confidence']}")
        print(f"Risk Tier: {data['decision']['risk_tier']}")
        print(f"Anomaly Score: {data['anomaly_score']}")
        print(f"Twins Found: {len(data['twins'])}")
        
        assert "twins" in data
        assert len(data['twins']) > 0
        assert "decision" in data
        assert "anomaly_score" in data
        
        # Verify twins are sorted by similarity
        twins = data['twins']
        sims = [t['similarity'] for t in twins]
        assert sims == sorted(sims, reverse=True), "Twins not sorted by similarity"
        
        print("PASS: Process application")
    except Exception as e:
        print(f"FAIL: Process application - {str(e)}")

def test_data_source():
    print("\nTesting Data Source Info...")
    try:
        response = requests.get(f"{BASE_URL}/data-source")
        response.raise_for_status()
        data = response.json()
        print(f"Data Source: {data}")
        assert "count" in data
        print("PASS: Data source info")
    except Exception as e:
        print(f"FAIL: Data source info - {str(e)}")

if __name__ == "__main__":
    print("Starting backend tests...")
    # Wait a bit for server to start if running immediately after startup
    time.sleep(1)
    
    test_api_status()
    test_reset_data()
    test_data_source()
    test_process_application()
    print("\nTests completed.")
