#!/bin/bash

echo -e "\033[0;32mStarting Multi-Agent AI System for Workshop...\033[0m"

# Activate virtual environment
source ./multi_agent/bin/activate

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo -e "\033[0;31m❌ uvicorn not found. Make sure your venv is activated and dependencies are installed.\033[0m"
    exit 1
fi

# 1. Start Job Agent
echo -e "\033[0;33mStarting Job Agent on port 8001...\033[0m"
uvicorn agents.job_agent:app --host 127.0.0.1 --port 8001 &
JOB_PID=$!

# 2. Start Learning Agent
echo -e "\033[0;33mStarting Learning Agent on port 8002...\033[0m"
uvicorn agents.learning_agent:app --host 127.0.0.1 --port 8002 &
LEARNING_PID=$!

# 3. Start Coordinator Agent
echo -e "\033[0;33mStarting Coordinator Agent on port 8000...\033[0m"
uvicorn agents.coordinator:app --host 127.0.0.1 --port 8000 &
COORDINATOR_PID=$!

# Wait for APIs to be ready
echo "Waiting for agents to start..."
sleep 3

# 4. Start Streamlit
echo -e "\033[0;33mStarting Streamlit UI (Frontend)...\033[0m"
streamlit run frontend/app.py &
STREAMLIT_PID=$!

echo -e "\033[0;32m✅ All services started!\033[0m"
echo ""
echo "  Job Agent:      http://127.0.0.1:8001"
echo "  Learning Agent: http://127.0.0.1:8002"
echo "  Coordinator:    http://127.0.0.1:8000"
echo "  Streamlit UI:   http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services."

# When Ctrl+C is pressed, kill all background processes
trap "echo 'Stopping all services...'; kill $JOB_PID $LEARNING_PID $COORDINATOR_PID $STREAMLIT_PID 2>/dev/null; exit" SIGINT SIGTERM

# Keep script alive
wait