import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google_adk import Agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Learning Agent")

class LearningRequest(BaseModel):
    skills_needed: str

def search_course_catalog(skills: str) -> str:
    """Mock catalog search tool for finding relevant courses."""
    return f"Course Catalog Hits for [{skills}]: 1. Advanced {skills} Specialization on Coursera (4 months). 2. Complete {skills} Bootcamp by Udemy. 3. Certified {skills} Professional Exam Prep."

# Google ADK framework implementation
agent = Agent(
    model="gemini-1.5-flash",
    tools=[search_course_catalog],
    system_instruction="You are a specialized Learning Agent. Suggest learning paths based on skills needed formatting clearly with platforms."
)

@app.post("/api/courses")
async def find_courses(req: LearningRequest):
    prompt = f"Suggest learning paths for skills: {req.skills_needed}."
    try:
        # ADK invocation
        response = agent.invoke(prompt)
        text_data = response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        text_data = f"Could not retrieve courses due to Agent Error: {str(e)}"
        
    return {"status": "success", "agent": "learning", "data": text_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
