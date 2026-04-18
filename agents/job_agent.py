import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk import Agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Job Agent")

class JobRequest(BaseModel):
    query: str
    location: str = "remote"

def search_job_database(query: str, location: str = "remote") -> str:
    """Mock database search tool for finding jobs based on query and location."""
    return f"DB Results for '{query}' in {location}: 1. Senior {query} ($100k-$150k), Key Skills: Python, Cloud. 2. Mid-level {query} ($80k-$110k), Key Skills: Data Analysis, Algorithms."

job_agent = Agent(
    name="JobAgent",
    model="gemini-2.5-flash",
    tools=[search_job_database],
    instruction="You are a specialized Job Agent. Use your tools to find and summarize job market data."
)

@app.post("/api/jobs")
async def find_jobs(req: JobRequest):
    prompt = f"Find job data for '{req.query}' in '{req.location}'."
    try:
        from google import genai
        from google.genai import types
        import os
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        resp = client.models.generate_content(
            model=job_agent.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=job_agent.instruction,
                tools=job_agent.tools
            )
        )
        # Handle tools if model explicitly requests
        if getattr(resp, 'function_calls', None):
            for tc in resp.function_calls:
                tool_func = next((t for t in job_agent.tools if t.__name__ == tc.name), None)
                if tool_func:
                    result = tool_func(**tc.args)
                    # For simplicity in sub-agents, we just execute and append context
                    resp = client.models.generate_content(
                        model=job_agent.model,
                        contents=[prompt, types.Part.from_function_response(name=tc.name, response={"result": str(result)})],
                        config=types.GenerateContentConfig(system_instruction=job_agent.instruction)
                    )
        text_data = resp.text
    except Exception as e:
        text_data = f"Could not retrieve jobs due to Agent Error: {str(e)}"
    
    return {"status": "success", "agent": "job", "data": text_data}
