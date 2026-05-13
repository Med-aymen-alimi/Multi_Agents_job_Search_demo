# Multi-Agent AI System: Career Navigator

Welcome to the Multi-Agent AI Career Navigator Workshop! This project demonstrates how to build a distributed architecture of AI agents that coordinate to perform complex tasks.

## 🚀 Overview

This repository establishes a **Multi-Agent (A2A)** platform powered by `google_adk` and the Gemini model. Instead of a monolithic application handling all prompts, this framework splits responsibilities across specialized, independent agents:

- **Coordinator Agent**: The main orchestrator. It receives the user's career queries, plans the required data gathering steps, delegates tasks via the A2A (Agent-to-Agent) protocol, and synthesizes the final strategic advice.
- **Job Agent**: A specialized microservice that simulates real-time job market searches based on role and location.
- **Learning Agent**: A specialized microservice that recommends tailored courses and learning paths to fill identified skills gaps.
- **Frontend App**: A sleek Streamlit UI where the end-user interacts seamlessly with the entire agent ecosystem.

## 📦 Architecture & Technologies

- **Python 3.9+**
- **FastAPI / Uvicorn**: For serving lightweight microservices per agent.
- **Streamlit**: For the interactive, chat-based frontend interface.
- **Google ADK** (`google-adk`): The core library enabling Agent abstractions and specialized Agent-to-Agent (`A2AClient`) communication protocols.
- **Gemini API**: The underlying LLM powering reasoning and synthesis tasks.

## ⚙️ A2A Protocol Implementation

In this repository, the true power of **Agent-to-Agent (A2A) protocol** is utilized. 
We've replaced standard monolithic dependencies with distributed `A2AClient` module tools.

This decoupling ensures that agents can scale out independently.

## 🚀 How to Run Locally

### 1. Prerequisites
- Add your `.env` file containing the `GEMINI_API_KEY`.
- Run: `pip install -r requirements.txt`

### 2. Start the System
You can launch the entire ecosystem using the provided batch scripts depending on your OS.

**Windows (PowerShell) or linux:**
```powershell
.\start_all.ps1
```

**Windows (CMD/Batch):**
```bat
start_all.bat
```
### 3. Usage
Once launched, the Streamlit app will open automatically in your browser (default: `http://localhost:8501`).
1. Type a career goal, e.g., *"I want to become a Senior AI Engineer."*
2. The UI sends the request via `A2AClient` to the **Coordinator Agent** (Port 8000).
3. The Coordinator intelligently runs the **Job Agent** (Port 8001) for market trends.
4. The Coordinator then runs the **Learning Agent** (Port 8002) for requisite learning paths.
5. The Coordinator synthesizes the data and streams it back to your interface!

---
*Happy Agentic Coding!* 🤖

