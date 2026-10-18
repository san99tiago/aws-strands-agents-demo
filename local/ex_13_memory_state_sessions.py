"""
EX-13: CONTEXT, STATE & SESSIONS - Short-term memory that survives restarts.

Slide: "Conversation Manager + Agent State + Session Manager"
Concepts:
    - conversation_manager: controls the CONTEXT WINDOW
        * SlidingWindowConversationManager(window_size=N)  -> keep last N messages
        * SummarizingConversationManager(...)               -> summarize old turns
    - agent.state: key-value JSON state, NOT sent to the model (great for IDs, flags, counters).
    - session_manager: persists messages + state (FileSessionManager local, S3SessionManager in AWS,
      or AgentCore Memory session manager). Same session_id -> conversation continues.

Run (twice to see persistence!):
    poetry run python local/ex_13_memory_state_sessions.py
"""

import os

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.session import FileSessionManager

SESSION_DIR = os.path.join(os.path.dirname(__file__), ".sessions")


def build_agent(session_id: str) -> Agent:
    return Agent(
        model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
        system_prompt="Eres el asistente de AnyBank. Responde en 1-2 frases en español.",
        conversation_manager=SlidingWindowConversationManager(window_size=20),
        session_manager=FileSessionManager(session_id=session_id, storage_dir=SESSION_DIR),
        state={"customer_id": "cust-001", "segment": "preferente"},
        callback_handler=None,
    )


agent = build_agent("cust-001-chat")
visits = (agent.state.get("visits") or 0) + 1
agent.state.set("visits", visits)
print(f"Visit #{visits} | messages restored from session: {len(agent.messages)}")

if visits == 1:
    print("A:", agent("Hola! Me llamo Laura y estoy ahorrando para un viaje a Japón en 2027."))
else:
    print("A:", agent("Hola de nuevo, te acuerdas cómo me llamo y para qué estoy ahorrando?"))

print("\nState (never sent to the LLM):", agent.state.get())
print(f"Session files at: {SESSION_DIR}  (delete the folder to reset)")
