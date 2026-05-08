#!/bin/bash
echo -e "\033[0;32mStarting Multi-Agent AI System for Workshop...\033[0m"

PYTHON="./multi_agent/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo -e "\033[0;31m❌ Python not found at $PYTHON. Is the venv created?\033[0m"
    exit 1
fi

if ! $PYTHON -m uvicorn --version &>/dev/null; then
    echo -e "\033[0;31m❌ uvicorn not found in venv. Run:\033[0m"
    echo -e "\033[0;31m   source multi_agent/bin/activate && pip install -r requirements.txt\033[0m"
    exit 1
fi

echo -e "\033[0;33mStarting Project Mentor Agent on port 8001...\033[0m"
$PYTHON -m uvicorn agents.project_mentor_agent:app --host 127.0.0.1 --port 8001 &
MENTOR_PID=$!

echo -e "\033[0;33mStarting Learning Agent on port 8002...\033[0m"
$PYTHON -m uvicorn agents.learning_agent:app --host 127.0.0.1 --port 8002 &
LEARNING_PID=$!

echo -e "\033[0;33mStarting Coordinator Agent on port 8000...\033[0m"
$PYTHON -m uvicorn agents.coordinator:app --host 127.0.0.1 --port 8000 &
COORDINATOR_PID=$!

echo "Waiting for agents to start..."
sleep 3

echo -e "\033[0;33mStarting Streamlit UI (Frontend)...\033[0m"
$PYTHON -m streamlit run frontend/app.py &
STREAMLIT_PID=$!

echo -e "\033[0;32m✅ All services started!\033[0m"
echo ""
echo "  Project Mentor Agent: http://127.0.0.1:8001"
echo "  Learning Agent:       http://127.0.0.1:8002"
echo "  Coordinator:          http://127.0.0.1:8000"
echo "  Streamlit UI:         http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services."

trap "echo 'Stopping all services...'; kill $MENTOR_PID $LEARNING_PID $COORDINATOR_PID $STREAMLIT_PID 2>/dev/null; exit" SIGINT SIGTERM

wait
