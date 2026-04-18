# start_all.ps1
Write-Host "Starting Multi-Agent AI System for Workshop..." -ForegroundColor Green

# Define the paths (assuming current directory)
$dir = Get-Location

# 1. Start Job Agent on Port 8001
Write-Host "Starting Job Agent on port 8001..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn agents.job_agent:app --port 8001"

# 2. Start Learning Agent on Port 8002
Write-Host "Starting Learning Agent on port 8002..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn agents.learning_agent:app --port 8002"

# 3. Start Coordinator Agent on Port 8000
Write-Host "Starting Coordinator Agent on port 8000..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn agents.coordinator:app --port 8000"

# 4. Wait a few seconds for backends to initialize
Start-Sleep -Seconds 3

# 5. Start Streamlit App on default Port 8501
Write-Host "Starting Streamlit UI (Frontend)..." -ForegroundColor Yellow
Start-Process -FilePath "streamlit" -ArgumentList "run frontend/app.py"

Write-Host "All services have been started!" -ForegroundColor Green
Write-Host "Streamlit UI should open in your browser automatically." -ForegroundColor Green
Write-Host "Press Ctrl+C to close this window (you will need to manually stop the python processes in Task Manager if you close this script unexpectedly)." -ForegroundColor Green

# Keep script running to view output if needed
Read-Host "Press Enter to exit and leave processes running"
