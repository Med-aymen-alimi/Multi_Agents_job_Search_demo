# start_all.bat
@echo off
echo Starting Multi-Agent AI System for Workshop...

echo Starting Job Agent on port 8001...
start cmd /k "python -m uvicorn agents.job_agent:app --port 8001"

echo Starting Learning Agent on port 8002...
start cmd /k "python -m uvicorn agents.learning_agent:app --port 8002"

echo Starting Coordinator Agent on port 8000...
start cmd /k "python -m uvicorn agents.coordinator:app --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Streamlit UI (Frontend)...
start cmd /k "streamlit run frontend/app.py"

echo All services have been started! Each has its own terminal window.
echo Close the terminal windows to stop the services.
pause
