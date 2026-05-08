"""
agents/project_mentor_agent.py
Project Mentor Agent Microservice — port 8001
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

app = FastAPI(title="Project Mentor Agent — Port 8001")


# ── 1. Define the tool ────────────────────────────────────────────────────────

def analyze_project_specification(project_spec: str) -> dict:
    """
    Analyze a project specification and extract required skills, technologies,
    frameworks, tools, and important concepts needed to complete the project.

    Args:
        project_spec: The project description or specification provided by the user.

    Returns:
        A dict with a 'result' key containing the extracted skills and technologies.
    """
    data = (
        f"Project Analysis Results for: '{project_spec}'\n"
        f"Required Skills: Problem-solving, System Design, Testing, Documentation\n"
        f"Technologies: Determined by project scope and stack\n"
        f"Frameworks: Relevant frameworks based on project type\n"
        f"Tools: Version control (Git), CI/CD, containerization (Docker)\n"
        f"Key Concepts: Software architecture, API design, data modeling, security best practices"
    )
    return {"result": data}


# ── 2. Build the ADK Agent ────────────────────────────────────────────────────

project_mentor_agent = Agent(
    name="ProjectMentorAgent",
    model="gemini-flash-latest",
    tools=[analyze_project_specification],
    instruction=(
        "You are a specialized Project Mentor Agent. "
        "When given a project specification, ALWAYS call analyze_project_specification first, "
        "then extract and summarise: required skills, technologies, frameworks, tools, "
        "and important concepts needed to complete the project. "
        "Be concise and structured."
    ),
)


# ── 3. ADK Runner + Session Service ──────────────────────────────────────────

session_service = InMemorySessionService()
runner = Runner(
    agent=project_mentor_agent,
    app_name="project_mentor_agent_app",
    session_service=session_service,
)

APP_NAME = "project_mentor_agent_app"
USER_ID  = "workshop_user"


# ── 4. Helper: run one turn through ADK ──────────────────────────────────────

async def run_project_mentor_agent(prompt: str) -> str:
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
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    print("\n" + "="*60)
                    print(f"🛠️  [PROJECT MENTOR] TOOL CALL")
                    print(f"   Tool    : {part.function_call.name}")
                    print(f"   Params  : {dict(part.function_call.args)}")
                    print("="*60)
                if hasattr(part, "function_response") and part.function_response:
                    print("\n" + "-"*60)
                    print(f"🛠️  [PROJECT MENTOR] TOOL RESPONSE")
                    print(f"   Tool    : {part.function_response.name}")
                    print(f"   Returns : {str(part.function_response.response)[:300]}")
                    print("-"*60 + "\n")

        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    return final_text or "Project Mentor Agent produced no response."


# ── 5. FastAPI endpoint ───────────────────────────────────────────────────────

class ProjectRequest(BaseModel):
    project_spec: str


@app.post("/api/projects")
async def analyze_project(req: ProjectRequest):
    prompt = f"Analyze the following project specification and extract required skills, technologies, frameworks, tools, and key concepts: {req.project_spec}"
    try:
        result = await run_project_mentor_agent(prompt)
    except Exception as e:
        result = f"Project Mentor Agent error: {str(e)}"
    return {"status": "success", "agent": "project_mentor", "data": result}


if __name__ == "__main__":
    uvicorn.run("agents.project_mentor_agent:app", host="127.0.0.1", port=8001, reload=True)