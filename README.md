# Multi-Agent AI System: Project Mentor

Welcome to the Multi-Agent AI Project Mentor Workshop! This project demonstrates how to build a distributed architecture of AI agents that coordinate to help users analyze, plan, and successfully build technical projects.

---

# 🚀 Overview

This repository establishes a **Multi-Agent (A2A)** platform powered by `google_adk` and the Gemini model. Instead of relying on a monolithic application to handle all prompts, this framework distributes responsibilities across specialized, independent agents.

The system is designed to transform a user's project idea into:

* a structured technical analysis,
* a required skills roadmap,
* and a personalized learning path.

---

# 🤖 Agent Ecosystem

## Coordinator Agent

The main orchestrator of the system.

Responsibilities:

* Receives the user's project specifications
* Understands technical goals and requirements
* Delegates tasks using the A2A (Agent-to-Agent) protocol
* Synthesizes all agent outputs into a cohesive project roadmap

---

## Project Mentor Agent

A specialized technical analysis microservice.

Responsibilities:

* Analyzes project specifications
* Extracts:

  * required skills
  * programming languages
  * frameworks
  * tools
  * APIs
  * architectural concepts
* Identifies technical requirements and implementation challenges

---

## Learning Agent

A specialized learning recommendation microservice.

Responsibilities:

* Receives required skills/topics from the Coordinator Agent
* Recommends:

  * courses
  * tutorials
  * documentation
  * learning paths
* Helps users efficiently acquire the knowledge needed to build their projects

---

## Frontend App

A sleek Streamlit-based UI where users interact seamlessly with the entire multi-agent ecosystem.

Users can:

* Describe project ideas
* Receive technical analysis
* Discover required technologies
* Get personalized learning recommendations
* Follow structured development roadmaps

---

# 📦 Architecture & Technologies

* **Python 3.9+**
* **FastAPI / Uvicorn**

  * Lightweight microservices for each agent
* **Streamlit**

  * Interactive chat-based frontend interface
* **Google ADK (`google-adk`)**

  * Core framework enabling Agent abstractions and Agent-to-Agent (`A2AClient`) communication
* **Gemini API**

  * Underlying LLM powering reasoning, orchestration, and synthesis

---

# ⚙️ A2A Protocol Implementation

This repository demonstrates the power of a true **Agent-to-Agent (A2A)** architecture.

Instead of using tightly coupled monolithic logic, agents communicate independently through distributed `A2AClient` protocols.

### Coordinator Agent

* Uses `A2AClient` from `google_adk.a2a`
* Orchestrates communication between specialized agents
* Routes project specifications dynamically

### Streamlit App

* Uses the A2A protocol to communicate with the Coordinator Agent
* Provides a clean and responsive user experience

This architecture enables:

* scalability
* modularity
* independent agent evolution
* cleaner separation of responsibilities

---

# 🚀 How to Run Locally

## 1. Prerequisites

Create a `.env` file containing your API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Start the System

You can launch the entire ecosystem using the provided startup scripts depending on your operating system.

## Windows (PowerShell)

```powershell
.\start_all.ps1
```

---

## Windows (CMD / Batch)

```bat
start_all.bat
```

---

## Ubuntu / Linux / macOS

Make the script executable:

```bash
chmod +x start_all.sh
```

Run the agents:

```bash
./start_all.sh
```

---

# 💡 Usage

Once launched, the Streamlit app will automatically open in your browser:

```text
http://localhost:8501
```

---

## Example Workflow

1. The user submits a project idea:

> "I want to build an AI-powered task management SaaS platform."

2. The Streamlit UI sends the request via `A2AClient` to the **Coordinator Agent** (Port 8000)

3. The Coordinator invokes the **Project Mentor Agent** (Port 8001) to:

   * analyze the project
   * identify required technologies
   * extract skills and architecture requirements

4. The Coordinator invokes the **Learning Agent** (Port 8002) to generate learning recommendations for the identified skills

5. The Coordinator synthesizes all outputs into:

   * a project roadmap
   * required technologies
   * learning guidance
   * implementation recommendations

6. The final response is streamed back to the user interface

---

# 🎯 Project Goals

This system aims to:

* Help developers transform ideas into executable projects
* Reduce technical overwhelm
* Provide personalized technical mentorship
* Accelerate learning and implementation
* Demonstrate scalable Multi-Agent AI architectures using A2A protocols

---

# 🧠 Example Use Cases

* AI SaaS applications
* Full-stack web platforms
* Mobile applications
* Cloud-native systems
* DevOps automation tools
* Machine learning projects
* Portfolio projects
* Startup MVP planning

---

# 📌 Future Improvements

Potential enhancements include:

* Architecture diagram generation
* Code scaffold generation
* GitHub integration
* Deployment automation guidance
* Team collaboration support
* Persistent project memory
* Multi-project tracking

---

# 🤝 Contributing

Contributions, improvements, and experimentation are welcome!

Feel free to:

* improve agent orchestration
* add new specialized agents
* optimize prompts
* enhance the frontend experience
* integrate external tools/services

---

# 📜 License

This project is intended for educational, research, and experimentation purposes.

---

*Happy Agentic Building!* 🤖
