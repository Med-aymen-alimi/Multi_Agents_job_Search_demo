import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google_adk.a2a import A2AClient
from google_adk import Agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Coordinator Agent")

class CoordinatorRequest(BaseModel):
    user_message: str

def request_job_market_data(domain: str) -> str:
    """Tool to request job market analysis from the external Job Agent microservice."""
    try:
        client = A2AClient(endpoint="http://localhost:8001/api/jobs")
        resp = client.run({"query": domain, "location": "remote"})
        return resp.get("data", "No job data found")
    except Exception as e:
        return f"Error contacting Job Agent: {str(e)}"

def request_learning_courses(skills: str) -> str:
    """Tool to request course recommendations from the external Learning Agent microservice."""
    try:
        client = A2AClient(endpoint="http://localhost:8002/api/courses")
        resp = client.run({"skills_needed": skills})
        return resp.get("data", "No learning data found")
    except Exception as e:
        return f"Error contacting Learning Agent: {str(e)}"

# Google ADK framework implementation
agent = Agent(
    model="gemini-3.1-flash-lite",
    tools=[request_job_market_data, request_learning_courses],
    system_instruction="""You are the Career Coordinator Agent.
    1. Extract the career domain and use the `request_job_market_data` tool.
    2. Read the results from step 1 to figure out what skills are in demand.
    3. Use the `request_learning_courses` tool with those specific skills.
    4. Synthesize all the tool results into a cohesive, encouraging Markdown career game plan."""
)

@app.post("/api/chat")
async def chat(req: CoordinatorRequest):
    try:
        # ADK invocation handles the tool routing automatically
        response = agent.run(req.user_message)
        final_response = response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
         final_response = f"Agent orchestration error: {str(e)}"
         
    return {"status": "success", "agent": "coordinator", "response": final_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
