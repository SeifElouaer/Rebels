@echo off
setlocal
title CreditTwin Launcher
cd /d %~dp0

echo ============================================================
echo                CreditTwin: Financial Twin Engine
echo ============================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

:: 2. Check dependencies (Initial Setup)
python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Missing dependencies. Running setup...
    python setup_project.py
    if %errorlevel% neq 0 (
        echo [ERROR] Setup failed. Please check the errors above.
        pause
        exit /b
    )
)

:: 3. Start Qdrant (via Docker)
echo [1/2] Attempting to start/run Qdrant...
docker start qdrant >nul 2>&1 || (
    echo [INFO] Qdrant container not found or stopped. Trying to run new instance...
    docker run -d -p 6333:6333 --name qdrant qdrant/qdrant >nul 2>&1
)

if %errorlevel% neq 0 (
    echo [WARNING] Could not start Qdrant via Docker. 
    echo Ensure Docker Desktop is running.
) else (
    echo [SUCCESS] Qdrant is active.
)

echo.
echo [2/2] Starting API Server...
echo 📍 Access at: http://localhost:5000
echo.

python Engine/app.py

echo.
echo Server stopped.
pause
