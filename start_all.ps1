Write-Host "Starting Multi-Agent AI System for Workshop..." -ForegroundColor Green

# Path to your virtual environment
$venvPath = ".\adk_wokrsohp\Scripts"
$python = "$venvPath\python.exe"
$streamlit = "$venvPath\streamlit.exe"

# Check if venv exists
if (!(Test-Path $python)) {
    Write-Host "❌ Virtual environment not found at $python" -ForegroundColor Red
    exit
}

# 1. Start Job Agent
Write-Host "Starting Job Agent on port 8001..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $python -ArgumentList "-m uvicorn agents.job_agent:app --host 127.0.0.1 --port 8001"

# 2. Start Learning Agent
Write-Host "Starting Learning Agent on port 8002..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $python -ArgumentList "-m uvicorn agents.learning_agent:app --host 127.0.0.1 --port 8002"

# 3. Start Coordinator Agent
Write-Host "Starting Coordinator Agent on port 8000..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $python -ArgumentList "-m uvicorn agents.coordinator:app --host 127.0.0.1 --port 8000"

# Wait for APIs
Start-Sleep -Seconds 3

# 4. Start Streamlit
Write-Host "Starting Streamlit UI (Frontend)..." -ForegroundColor Yellow
Start-Process -FilePath $streamlit -ArgumentList "run frontend/app.py"

Write-Host "✅ All services started using your virtual environment!" -ForegroundColor Green

# Keep script alive
Read-Host "Press Enter to exit (services will keep running)"