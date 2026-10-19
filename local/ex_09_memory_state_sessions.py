"""
EX-09: MEMORY, STATE & SESSIONS - The 4 ways an agent "remembers".

Slide: "Memoria, estado y sesiones"
Concepts:
    1. Conversation Manager -> what fits in the CONTEXT WINDOW now (sliding window / summarizing).
    2. Agent State          -> key-value JSON for your code (IDs, flags). NEVER sent to the LLM.
    3. Session Manager      -> persists messages + state of ONE conversation (File, S3, AgentCore Memory).
    4. Memory Manager       -> LONG-TERM memory across sessions: facts are stored and injected
                               into future conversations (FileMemoryStore, Bedrock KB, AgentCore Memory).

Run:
    poetry run python local/ex_09_memory_state_sessions.py
"""

import os

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.memory import MemoryManager
from strands.models import BedrockModel
from strands.session import FileSessionManager
from strands.storage.local_file_storage import LocalFileStorage
from strands.vended_memory_stores import FileMemoryStore

BASE = os.path.join(os.path.dirname(__file__), ".agent")

# 4. Long-term memory, shared by every session of this customer
memory = MemoryManager(
    stores=[FileMemoryStore(name="gustos-santi", storage=LocalFileStorage(BASE))],
    add_tool_config=True,  # the agent gets an "add_memory" tool to save durable facts
)


def rufus_agent(session_id: str) -> Agent:
    return Agent(
        model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
        system_prompt=(
            "Eres Rufus, el coach financiero de RufusBank. Guarda en memoria cada gusto o meta del cliente. "
            "Responde en español, cercano y en máximo 6 líneas."
        ),
        conversation_manager=SlidingWindowConversationManager(window_size=10),  # 1. context window
        state={"cliente": "Santi", "excedente_mensual_cop": 2_500_000},  # 2. agent state
        session_manager=FileSessionManager(session_id=session_id, storage_dir=os.path.join(BASE, "sessions")),  # 3.
        memory_manager=memory,  # 4. long-term memory
        callback_handler=None,
    )


# ---- Session 1 (e.g. Monday, in the app)
monday = rufus_agent("santi-lunes")
for msg in [
    "Hola Rufus, soy Santi. Quiero comprar un Play 5 para jugar GTA6.",
    "También tengo muchas ganas de ir a conocer Cartagena.",
    "Y ante todo, me encantan los eventos de tecnología.",
]:
    print(f"\nSANTI > {msg}\nRUFUS > {monday(msg)}")

# ---- Session 2 (e.g. Friday, a NEW conversation): the context is empty, the long-term memory is not
friday = rufus_agent("santi-viernes")
excedente = friday.state.get("excedente_mensual_cop")
print("\n" + "=" * 70 + f"\nNEW SESSION | messages in context: {len(friday.messages)} | state: {friday.state.get()}")
print(friday(
    f"Hola de nuevo. Este mes me sobran {excedente:,} COP. ¿Qué me recomiendas según TODOS mis gustos guardados? "
    "Incluye un plan para volverme experto en agentes (por ejemplo en GenAI University) y termina con "
    "'¡Vamos con toda Santi, crack!' y una frase motivacional que compare los LLMs y los agentes con lograr una meta."
))
print(f"\nMemory + sessions saved at: {BASE}  (delete the folder to reset)")
