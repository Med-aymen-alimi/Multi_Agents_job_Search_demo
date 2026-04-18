import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_weather(location: str) -> str:
    """Gets the weather for a location."""
    return "Sunny and glorious"

chat = client.chats.create(model='gemini-3.1-flash-lite', config=types.GenerateContentConfig(tools=[get_weather]))
resp = chat.send_message('what is the weather in sf?')
print(resp.function_calls)
for tc in resp.function_calls:
    print(tc.name, tc.args)
