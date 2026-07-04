@echo off
:: Kavalar Local Launch Script (Windows Command Prompt)
echo ==================================================
echo Starting Kavalar Local Setup ^& Launch
echo ==================================================

:: Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Check Node
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    pause
    exit /b 1
)

:: Set up Backend Virtual Environment
echo Setting up Python virtual environment in backend...
cd backend
if not exist "venv" (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

:: Create default .env if it doesn't exist
if not exist ".env" (
    echo Creating default backend .env file...
    echo DATABASE_URL=sqlite:///./kavalar.db>.env
    echo MODEL_NAME=llama-3.3-70b-versatile>>.env
    echo GROQ_API_KEY=your_groq_api_key_here>>.env
)

:: Train the Anomaly Detector Baseline
echo Training baseline profile...
python train_baseline.py
if %errorlevel% neq 0 (
    echo ERROR: Baseline training failed.
    pause
    exit /b 1
)

:: Start Backend in a separate window
echo Launching FastAPI backend in a new window...
start "Kavalar Backend Server" cmd /k "venv\Scripts\activate && uvicorn main:app --port 8000 --reload"

cd ..

:: Set up Frontend
echo Installing frontend dependencies...
cd frontend
call npm install

:: Start Frontend
echo Launching Next.js frontend on http://localhost:3000...
echo ==================================================
echo Kavalar is now starting up!
echo Backend:  http://localhost:8000 (Swagger docs at /docs)
echo Frontend: http://localhost:3000
echo Close the terminals to stop the processes.
echo ==================================================
npm run dev

cd ..
