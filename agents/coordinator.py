"""
agents/coordinator.py
Coordinator Agent Microservice — port 8000

Uses Google ADK Agent + Runner + InMemorySessionService.
Calls Job Agent (8001) and Learning Agent (8002) via A2A HTTP protocol
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

def request_job_market_data(domain: str) -> dict:
    """
    Contact the Job Agent microservice to get job market analysis for a career domain.

    Args:
        domain: The career domain or job title to research (e.g. 'Machine Learning').

    Returns:
        A dict with a 'result' key containing the job market summary.
    """
    try:
        client = A2AClient(endpoint="http://127.0.0.1:8001/api/jobs")
        resp = client.call({"query": domain, "location": "remote"})
        return {"result": resp.get("data", "No job data returned.")}
    except requests.exceptions.ConnectionError:
        return {"result": "ERROR: Job Agent not reachable on port 8001. Is it running?"}
    except Exception as e:
        return {"result": f"ERROR calling Job Agent: {str(e)}"}


def request_learning_courses(skills: str) -> dict:
    """
    Contact the Learning Agent microservice to get course recommendations for a set of skills.

    Args:
        skills: Comma-separated skills identified from job market data
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
    tools=[request_job_market_data, request_learning_courses],
    instruction="""You are the Career Coordinator Agent that orchestrates a multi-agent system.

For every user request, follow these steps IN ORDER:

STEP 1 — Extract the career domain from the user's message.

STEP 2 — Call `request_job_market_data` with the domain to get job market analysis
          from the Job Agent microservice.

STEP 3 — Analyse the job data and identify the top 3-5 most in-demand skills.

STEP 4 — Call `request_learning_courses` with those specific skills (comma-separated)
          to get course recommendations from the Learning Agent microservice.

STEP 5 — Synthesise EVERYTHING into a well-structured Markdown career game plan:
  - ## 🎯 Career Overview
  - ## 💼 Job Market Insights  (from Step 2)
  - ## 🔑 Top Skills in Demand (from Step 3)
  - ## 📚 Your Learning Roadmap (from Step 4)
  - ## 🚀 Next Steps (your advice)

Be encouraging, concrete, and actionable. Always use BOTH tools before writing your answer.""",
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
                    print(f"[Coordinator] → Calling tool: {part.function_call.name}")
                if hasattr(part, "function_response") and part.function_response:
                    print(f"[Coordinator] ← Tool result: {str(part.function_response.response)[:100]}…")

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