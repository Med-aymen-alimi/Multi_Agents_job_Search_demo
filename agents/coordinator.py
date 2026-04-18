import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk import Agent
from .job_agent import job_agent
from .learning_agent import learning_agent
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI(title="Coordinator Agent")

class CoordinatorRequest(BaseModel):
    user_message: str

class A2AClient:
    """Agent-to-Agent (A2A) HTTP Client Protocol wrapper."""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def run(self, payload: dict) -> dict:
        response = requests.post(self.endpoint, json=payload)
        response.raise_for_status()
        return response.json()

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

coordinator_agent = Agent(
    name="CoordinatorAgent",
    model="gemini-2.5-flash",
    tools=[request_job_market_data, request_learning_courses],
    sub_agents=[job_agent, learning_agent],
    instruction="""You are the Career Coordinator Agent.
    1. Extract the career domain from the user's message.
    2. Formulate a query and use JobAgent to get market data for that domain.
    3. Read the market data results to figure out what top skills are in demand.
    4. Pass those specific skills to LearningAgent to get course recommendations.
    5. Synthesize all the sub-agent results into a cohesive, encouraging Markdown career game plan."""
)

@app.post("/api/chat")
async def chat(req: CoordinatorRequest):
    try:
        from google import genai
        from google.genai import types
        import os
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        chat_session = client.chats.create(
            model=coordinator_agent.model, 
            config=types.GenerateContentConfig(
                system_instruction=coordinator_agent.instruction,
                tools=coordinator_agent.tools
            )
        )
        resp = chat_session.send_message(req.user_message)
        
        # Handle the tools (A2A endpoints) if Gemini requests them
        if resp.function_calls:
            for tc in resp.function_calls:
                tool_func = next((t for t in coordinator_agent.tools if t.__name__ == tc.name), None)
                if tool_func:
                    result = tool_func(**tc.args)
                    resp = chat_session.send_message(
                        types.Content(role="user", parts=[types.Part.from_function_response(name=tc.name, response={"result": str(result)})])
                    )
                    
        final_response = resp.text
    except Exception as e:
         final_response = f"Agent orchestration error: {str(e)}"
         
    return {"status": "success", "agent": "coordinator", "response": final_response}
