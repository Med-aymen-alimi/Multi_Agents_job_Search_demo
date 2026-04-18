import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google_adk import Agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Job Agent")

class JobRequest(BaseModel):
    query: str
    location: str = "remote"

def search_job_database(query: str, location: str) -> str:
    """Mock database search tool for finding jobs based on query and location."""
    return f"DB Results for '{query}' in {location}: 1. Senior {query} ($100k-$150k), Key Skills: Python, Cloud. 2. Mid-level {query} ($80k-$110k), Key Skills: Data Analysis, Algorithms."

# Google ADK framework implementation
agent = Agent(
    model="gemini-1.5-flash",
    tools=[search_job_database],
    system_instruction="You are a specialized Job Agent. Use your tools to find and summarize job market data."
)

@app.post("/api/jobs")
async def find_jobs(req: JobRequest):
    prompt = f"Find job data for '{req.query}' in '{req.location}'."
    try:
        # ADK invocation
        response = agent.invoke(prompt)
        text_data = response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        text_data = f"Could not retrieve jobs due to Agent Error: {str(e)}"
    
    return {"status": "success", "agent": "job", "data": text_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
