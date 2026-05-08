"""
agents/learning_agent.py
Learning Agent Microservice — port 8002
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

app = FastAPI(title="Learning Agent — Port 8002")

# ── 1. Define the tool ────────────────────────────────────────────────────────

def search_course_catalog(skills: str) -> dict:
    """
    Search the course catalog for learning resources matching the required skills.

    Args:
        skills: Comma-separated list of skills to find courses for
                (e.g. 'Python, Machine Learning, SQL').

    Returns:
        A dict with a 'result' key containing the course recommendations.
    """
    data = (
        f"Course Catalog Results for skills: [{skills}]\n"
        f"1. 'Complete {skills} Bootcamp' — Udemy — 40 hrs — ★4.7 — $15\n"
        f"2. '{skills} Specialization' — Coursera (deeplearning.ai) — 4 months — ★4.8 — Free audit\n"
        f"3. '{skills} Professional Certificate' — LinkedIn Learning — 3 months — ★4.6 — Subscription\n"
        f"4. 'Hands-on {skills} Projects' — Kaggle — Self-paced — Free"
    )
    return {"result": data}


# ── 2. Build the ADK Agent ────────────────────────────────────────────────────

learning_agent = Agent(
    name="LearningAgent",
    model="gemini-flash-latest",
    tools=[search_course_catalog],
    instruction=(
        "You are a specialized Learning Path Agent. "
        "When given a list of skills, ALWAYS call search_course_catalog first, "
        "then present a clear, structured learning roadmap with platforms, "
        "estimated durations, and cost. Be encouraging and practical."
    ),
)

# ── 3. ADK Runner + Session Service ──────────────────────────────────────────

session_service = InMemorySessionService()
runner = Runner(
    agent=learning_agent,
    app_name="learning_agent_app",
    session_service=session_service,
)

APP_NAME = "learning_agent_app"
USER_ID  = "workshop_user"


# ── 4. Helper: run one turn through ADK ──────────────────────────────────────

async def run_learning_agent(prompt: str) -> str:
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

    return final_text or "Learning Agent produced no response."


# ── 5. FastAPI endpoint ───────────────────────────────────────────────────────

class LearningRequest(BaseModel):
    skills_needed: str


@app.post("/api/courses")
async def find_courses(req: LearningRequest):
    prompt = f"Suggest a learning path for the following skills: {req.skills_needed}."
    try:
        result = await run_learning_agent(prompt)
    except Exception as e:
        result = f"Learning Agent error: {str(e)}"
    return {"status": "success", "agent": "learning", "data": result}


if __name__ == "__main__":
    uvicorn.run("agents.learning_agent:app", host="127.0.0.1", port=8002, reload=True)