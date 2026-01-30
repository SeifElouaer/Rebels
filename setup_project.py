import os
import sys
import subprocess
import shutil

def run_command(command, cwd=None):
    print(f"🚀 Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        return False

def setup():
    print("=" * 70)
    print("CreditTwin Project Setup".center(70))
    print("=" * 70)

    # 1. Check for .env
    if not os.path.exists(".env"):
        print("📝 Creating .env from .env.example...")
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
        else:
            with open(".env", "w") as f:
                f.write("QDRANT_HOST=localhost\nQDRANT_PORT=6333\n")

    # 2. Install dependencies
    print("📦 Installing dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        print("❌ Critical Error: Dependency installation failed.")
        sys.exit(1)

    # 3. Check if Qdrant is accessible (optional check)
    print("🔍 Checking if Qdrant is accessible...")
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        host = os.getenv("QDRANT_HOST", "localhost")
        port = os.getenv("QDRANT_PORT", "6333")
        response = requests.get(f"http://{host}:{port}/healthz", timeout=2)
        if response.status_code == 200:
            print("   ✓ Qdrant is UP")
        else:
            print(f"   ⚠️  Qdrant returned status {response.status_code}")
    except Exception:
        print("   ❌ Qdrant is NOT accessible. Please start Qdrant using:")
        print("      docker run -p 6333:6333 qdrant/qdrant")

    # 4. Load data into SQLite
    print("\n🗄️  Initializing SQLite Database...")
    if run_command([sys.executable, "Engine/data_loader.py"]):
        print("   ✓ Database initialized")
    else:
        print("   ❌ Critical Error: Database initialization failed")
        sys.exit(1)

    # 5. Build Vector Store
    print("\n🧠 Building Vector Store (requires Qdrant)...")
    if run_command([sys.executable, "Engine/buildvector_store.py"]):
        print("   ✓ Vector store built")
    else:
        print("   ❌ Critical Error: Vector store build failed (is Qdrant running?)")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Setup Complete!".center(70))
    print("=" * 70)
    print("\nTo start the API server, run:")
    print(f"   {sys.executable} Engine/app.py")
    print("\nHappy testing!")

if __name__ == "__main__":
    setup()
