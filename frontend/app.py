import streamlit as st
from google_adk.a2a import A2AClient

st.set_page_config(page_title="AI Career Navigator", layout="centered", page_icon="🚀")

st.title("🚀 Multi-Agent AI System: Career Navigator")
st.markdown("""
Welcome to the career improvement system! This workshop demonstrates an **A2A (Agent-to-Agent)** framework.
- **Coordinator Agent**: Orchestrates and synthesizes.
- **Job Agent**: Finds current market opportunities.
- **Learning Agent**: Suggests courses and skills.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., I want to become a Machine Learning Engineer"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Multi-Agent System is working: Coordinator is delegating to Job Agent & Learning Agent..."):
            try:
                # Call Coordinator service via A2A Protocol
                coordinator = A2AClient(endpoint="http://localhost:8000/api/chat")
                response = coordinator.invoke({"user_message": prompt})
                
                # Based on the custom format in coordinator
                if response:
                    answer = response.get("response", "Error getting answer from Coordinator.")
                else:
                    answer = "Error: Coordinator returned no response."
            except Exception as e:
                answer = f"**Connection Error:** Could not reach the Coordinator Agent. Ensure all services are running.\n`{str(e)}`"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
