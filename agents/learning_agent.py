import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk import Agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Learning Agent")

class LearningRequest(BaseModel):
    skills_needed: str

def search_course_catalog(skills: str) -> str:
    """Mock catalog search tool for finding relevant courses."""
    return f"Course Catalog Hits for [{skills}]: 1. Advanced {skills} Specialization on Coursera (4 months). 2. Complete {skills} Bootcamp by Udemy. 3. Certified {skills} Professional Exam Prep."

learning_agent = Agent(
    name="LearningAgent",
    model="gemini-2.5-flash",
    tools=[search_course_catalog],
    instruction="You are a specialized Learning Agent. Suggest learning paths based on skills needed formatting clearly with platforms."
)

@app.post("/api/courses")
async def find_courses(req: LearningRequest):
    prompt = f"Suggest learning paths for skills: {req.skills_needed}."
    try:
        from google import genai
        from google.genai import types
        import os
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        resp = client.models.generate_content(
            model=learning_agent.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=learning_agent.instruction,
                tools=learning_agent.tools
            )
        )
        if getattr(resp, 'function_calls', None):
            for tc in resp.function_calls:
                tool_func = next((t for t in learning_agent.tools if t.__name__ == tc.name), None)
                if tool_func:
                    result = tool_func(**tc.args)
                    resp = client.models.generate_content(
                        model=learning_agent.model,
                        contents=[prompt, types.Part.from_function_response(name=tc.name, response={"result": str(result)})],
                        config=types.GenerateContentConfig(system_instruction=learning_agent.instruction)
                    )
        text_data = resp.text
    except Exception as e:
        text_data = f"Could not retrieve courses due to Agent Error: {str(e)}"
        
    return {"status": "success", "agent": "learning", "data": text_data}
