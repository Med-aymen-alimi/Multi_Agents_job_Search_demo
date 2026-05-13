"""
agents/job_agent.py
Job Agent Microservice — port 8001
Uses Google ADK Agent + Runner + InMemorySessionService properly.
"""

import os
import uuid
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

app = FastAPI(title="Job Agent — Port 8001")

# ── 1. Define the tool ────────────────────────────────────────────────────────

def search_job_database(query: str, location: str = "remote") -> dict:
    """
    Search the job database for openings matching a query and location.

    Args:
        query:    Job title or domain to search for (e.g. 'Data Science').
        location: Preferred work location (default 'remote').

    Returns:
        A dict with a 'result' key containing the job listings summary.
    """
    data = (
        f"Job Market Results for '{query}' in '{location}':\n"
        f"1. Senior {query} Engineer — $110k-$150k — Skills: Python, Cloud, Docker\n"
        f"2. Mid-level {query} Analyst — $80k-$110k — Skills: SQL, Statistics, Tableau\n"
        f"3. {query} Consultant (Freelance) — $70-$120/hr — Skills: Communication, Strategy"
    )
    return {"result": data}


# ── 2. Build the ADK Agent ────────────────────────────────────────────────────

job_agent = Agent(
    name="JobAgent",
    model="gemini-flash-latest",
    tools=[search_job_database],
    instruction=(
        "You are a specialized Job Market Agent. "
        "When given a career domain, ALWAYS call search_job_database first, "
        "then summarise the top opportunities and the key skills in demand. "
        "Be concise and structured."
    ),
)

# ── 3. ADK Runner + Session Service ──────────────────────────────────────────

session_service = InMemorySessionService()
runner = Runner(
    agent=job_agent,
    app_name="job_agent_app",
    session_service=session_service,
)

APP_NAME = "job_agent_app"
USER_ID  = "workshop_user"


# ── 4. Helper: run one turn through ADK ──────────────────────────────────────

async def run_job_agent(prompt: str) -> str:
    """Create a fresh session per request and run the agent."""
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
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    return final_text or "Job Agent produced no response."


# ── 5. FastAPI endpoint ───────────────────────────────────────────────────────

class JobRequest(BaseModel):
    query: str
    location: str = "remote"


@app.post("/api/jobs")
async def find_jobs(req: JobRequest):
    prompt = f"Find job market data for the domain '{req.query}' in '{req.location}'."
    try:
        result = await run_job_agent(prompt)
    except Exception as e:
        result = f"Job Agent error: {str(e)}"
    return {"status": "success", "agent": "job", "data": result}


if __name__ == "__main__":
    uvicorn.run("agents.job_agent:app", host="127.0.0.1", port=8001, reload=True)