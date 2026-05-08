"""
frontend/app.py
Streamlit UI for the Multi-Agent Project Learning Navigator system.
Connects to the Coordinator Agent via A2A HTTP on port 8000.
"""

import streamlit as st
import requests

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Project Learning Navigator",
    layout="centered",
    page_icon="🚀",
)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🚀 Multi-Agent AI Project Learning Navigator")
st.markdown("""
This system uses a **3-agent A2A (Agent-to-Agent) architecture** powered by **Google ADK**:

| Agent | Role | Port |
|---|---|---|
| 🧠 **Coordinator** | Orchestrates the full pipeline | 8000 |
| 🛠️ **Project Mentor Agent** | Analyses project specs & extracts required skills | 8001 |
| 📚 **Learning Agent** | Recommends courses & learning paths | 8002 |

Just describe your project below and the agents will collaborate to build your learning roadmap!
""")

st.divider()

# ── A2A Client ────────────────────────────────────────────────────────────────

class A2AClient:
    """Thin HTTP wrapper for calling agent microservices."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def run(self, payload: dict) -> dict:
        response = requests.post(self.endpoint, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()


# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render chat history ───────────────────────────────────────────────────────

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ────────────────────────────────────────────────────────────────

if prompt := st.chat_input("E.g., I want to build a real-time chat application using React and Node.js"):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call coordinator and show response
    with st.chat_message("assistant"):
        with st.spinner(
            "🤖 Agents collaborating: Coordinator → Project Mentor Agent → Learning Agent…"
        ):
            try:
                coordinator = A2AClient(endpoint="http://127.0.0.1:8000/api/chat")
                response = coordinator.run({"user_message": prompt})
                answer = response.get("response") or "⚠️ Coordinator returned an empty response."

            except requests.exceptions.ConnectionError:
                answer = (
                    "❌ **Connection Error** — Could not reach the Coordinator Agent.\n\n"
                    "Make sure all three agents are running:\n"
                    "```bash\n"
                    "uvicorn agents.project_mentor_agent:app --host 127.0.0.1 --port 8001\n"
                    "uvicorn agents.learning_agent:app --host 127.0.0.1 --port 8002\n"
                    "uvicorn agents.coordinator:app --host 127.0.0.1 --port 8000\n"
                    "```"
                )
            except requests.exceptions.Timeout:
                answer = (
                    "⏱️ **Timeout** — The agents took too long to respond. "
                    "Try again or check the terminal logs."
                )
            except Exception as e:
                answer = f"⚠️ **Unexpected Error:** `{str(e)}`"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Sidebar: service status checker ──────────────────────────────────────────

with st.sidebar:
    st.header("🔌 Agent Status")

    services = {
        "🧠 Coordinator (8000)":            "http://127.0.0.1:8000/docs",
        "🛠️ Project Mentor Agent (8001)":   "http://127.0.0.1:8001/docs",
        "📚 Learning Agent (8002)":          "http://127.0.0.1:8002/docs",
    }

    if st.button("Check All Services"):
        for name, url in services.items():
            try:
                r = requests.get(url, timeout=3)
                if r.status_code == 200:
                    st.success(f"{name} — ✅ Online")
                else:
                    st.warning(f"{name} — ⚠️ Status {r.status_code}")
            except Exception:
                st.error(f"{name} — ❌ Offline")

    st.divider()
    st.markdown("**How to start all agents:**")
    st.code(
        "uvicorn agents.project_mentor_agent:app --port 8001\n"
        "uvicorn agents.learning_agent:app --port 8002\n"
        "uvicorn agents.coordinator:app --port 8000\n"
        "streamlit run frontend/app.py",
        language="bash",
    )

    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()