"""
agents/coordinator.py
Coordinator Agent Microservice — port 8000

Uses Google ADK Agent + Runner + InMemorySessionService.
Calls Project Mentor Agent (8001) and Learning Agent (8002) via A2A HTTP protocol
as ADK tools, so the LLM decides when and how to call them.
"""

import os
import uuid
import uvicorn
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

app = FastAPI(title="Coordinator Agent — Port 8000")


# ── 1. A2A HTTP client ────────────────────────────────────────────────────────

class A2AClient:
    """Sends a JSON payload to a remote agent endpoint and returns its response."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def call(self, payload: dict) -> dict:
        response = requests.post(self.endpoint, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()


# ── 2. A2A Tool functions (registered as ADK tools) ──────────────────────────

def request_project_analysis(project_spec: str) -> dict:
    """
    Contact the Project Mentor Agent microservice to analyze a project specification
    and extract required skills, technologies, frameworks, tools, and key concepts.

    Args:
        project_spec: The project description or specification provided by the user.

    Returns:
        A dict with a 'result' key containing the project analysis summary.
    """
    try:
        client = A2AClient(endpoint="http://127.0.0.1:8001/api/projects")
        resp = client.call({"project_spec": project_spec})
        return {"result": resp.get("data", "No project analysis returned.")}
    except requests.exceptions.ConnectionError:
        return {"result": "ERROR: Project Mentor Agent not reachable on port 8001. Is it running?"}
    except Exception as e:
        return {"result": f"ERROR calling Project Mentor Agent: {str(e)}"}


def request_learning_courses(skills: str) -> dict:
    """
    Contact the Learning Agent microservice to get course recommendations for a set of skills.

    Args:
        skills: Comma-separated skills/technologies identified from the project analysis
                (e.g. 'Python, Docker, SQL').

    Returns:
        A dict with a 'result' key containing the learning path recommendations.
    """
    try:
        client = A2AClient(endpoint="http://127.0.0.1:8002/api/courses")
        resp = client.call({"skills_needed": skills})
        return {"result": resp.get("data", "No course data returned.")}
    except requests.exceptions.ConnectionError:
        return {"result": "ERROR: Learning Agent not reachable on port 8002. Is it running?"}
    except Exception as e:
        return {"result": f"ERROR calling Learning Agent: {str(e)}"}


# ── 3. Build the ADK Coordinator Agent ───────────────────────────────────────

coordinator_agent = Agent(
    name="CoordinatorAgent",
    model="gemini-flash-latest",
    tools=[request_project_analysis, request_learning_courses],
    instruction = """
You are the Career Coordinator Agent that orchestrates a multi-agent system.

Your role is to guide users in project-based learning by coordinating specialized agents.

---

## ⚠️ IMPORTANT RULE

If the user request does NOT clearly mention a project or project idea:
- DO NOT call any tools
- DO NOT assume or invent a project
- Respond normally by asking the user to describe a project idea before proceeding

Only proceed with tool usage if a project is explicitly mentioned.

---

## WORKFLOW (ONLY IF PROJECT EXISTS)

STEP 1 — Extract the project idea from the user message.

STEP 2 — Call `request_project_analysis(project_specification)`
to get required skills, technologies, frameworks, tools, and concepts
(from the Project Mentor Agent).

STEP 3 — Select the most important 3–5 skills from the analysis.

STEP 4 — Call `request_learning_courses(skills)`
using those selected skills (comma-separated)
(from the Learning Agent).

STEP 5 — Synthesize everything into a structured Markdown response:

## 🎯 Project Overview
## 🛠️ Project Analysis
## 🔑 Key Skills & Technologies
## 📚 Learning Roadmap
## 🚀 Next Steps

---

## STYLE

- Be clear, concise, and helpful
- Be structured but not verbose
- Focus on actionable guidance

---

## CONSTRAINTS

- Never call tools without a project mention
- Never hallucinate data
- Always follow the workflow order
""",
)

# ── 4. ADK Runner + Session Service ──────────────────────────────────────────

session_service = InMemorySessionService()
runner = Runner(
    agent=coordinator_agent,
    app_name="coordinator_app",
    session_service=session_service,
)

APP_NAME = "coordinator_app"
USER_ID  = "workshop_user"


# ── 5. Helper: run one turn through ADK ──────────────────────────────────────

async def run_coordinator(prompt: str) -> str:
    """Create a fresh session per request and run the coordinator agent."""
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):
        # Log intermediate tool calls for debugging
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    print("\n" + "="*60)
                    print(f"🧠 [COORDINATOR] TOOL CALL")
                    print(f"   Tool    : {part.function_call.name}")
                    print(f"   Params  : {dict(part.function_call.args)}")
                    print("="*60)
                if hasattr(part, "function_response") and part.function_response:
                    print("\n" + "-"*60)
                    print(f"🧠 [COORDINATOR] TOOL RESPONSE")
                    print(f"   Tool    : {part.function_response.name}")
                    print(f"   Returns : {str(part.function_response.response)[:300]}")
                    print("-"*60 + "\n")
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    return final_text or "Coordinator produced no response."


# ── 6. FastAPI endpoint ───────────────────────────────────────────────────────

class CoordinatorRequest(BaseModel):
    user_message: str


@app.post("/api/chat")
async def chat(req: CoordinatorRequest):
    try:
        result = await run_coordinator(req.user_message)
    except Exception as e:
        result = f"Coordinator error: {str(e)}"
    return {"status": "success", "agent": "coordinator", "response": result}


if __name__ == "__main__":
    uvicorn.run("agents.coordinator:app", host="127.0.0.1", port=8000, reload=True)