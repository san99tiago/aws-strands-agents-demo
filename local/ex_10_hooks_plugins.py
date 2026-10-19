"""
EX-10: HOOKS & PLUGINS - "Pit stops" in every lap of the agent loop.

Slide: "Hooks y plugins"
Concepts:
    - Lifecycle events: BeforeInvocation -> BeforeModelCall -> AfterModelCall -> BeforeToolCall
      -> AfterToolCall -> ... -> AfterInvocation.
    - Plugin: reusable bundle of @hook methods -> Agent(plugins=[...]).
    - agent.add_hook(callback, EventType): quick one-off hook.
    - Typical uses: audit logs (compliance), PII masking, cost tracking, rate limiting.

Run:
    poetry run python local/ex_10_hooks_plugins.py
"""

import re

from strands import Agent, tool
from strands.hooks import (
    AfterInvocationEvent,
    AfterModelCallEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeModelCallEvent,
    BeforeToolCallEvent,
)
from strands.models import BedrockModel
from strands.plugins import Plugin, hook


@tool
def datos_contacto(cliente_id: str) -> str:
    """Obtiene los datos de contacto de un cliente de RufusBank.

    Args:
        cliente_id: Identificador del cliente.
    """
    return f"Cliente {cliente_id}: email laura.gomez@mail.com, celular 3001234567, cédula 1037654321"


class PitStopPlugin(Plugin):
    """Audit every 'pit stop' of the agent loop and mask PII before it reaches the model."""

    name = "rufusbank-pit-stops"

    @hook
    def salida(self, event: BeforeInvocationEvent) -> None:
        print("🏁 [BeforeInvocation] arranca la carrera")

    @hook
    def antes_modelo(self, event: BeforeModelCallEvent) -> None:
        print("🏎️  [BeforeModelCall] el LLM piensa...")

    @hook
    def despues_modelo(self, event: AfterModelCallEvent) -> None:
        print("🧠 [AfterModelCall] el LLM decidió")

    @hook
    def antes_tool(self, event: BeforeToolCallEvent) -> None:
        print(f"🔧 [BeforeToolCall] pit stop -> {event.tool_use['name']}({event.tool_use['input']})")

    @hook
    def despues_tool(self, event: AfterToolCallEvent) -> None:
        for block in event.result["content"]:  # mask PII BEFORE it goes back to the model
            if "text" in block:
                block["text"] = re.sub(r"\b\d{7,10}\b", "**********", re.sub(r"[\w.]+@[\w.]+", "***@***", block["text"]))
        print(f"🛡️  [AfterToolCall] resultado enmascarado -> {event.result['content'][0]['text']}")


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[datos_contacto],
    plugins=[PitStopPlugin()],
    system_prompt="Eres un agente de back-office de RufusBank. Responde en español.",
    callback_handler=None,
)
agent.add_hook(lambda e: print("🏆 [AfterInvocation] ¡meta!"), AfterInvocationEvent)

print("\nRESPUESTA FINAL >", agent("Dame los datos de contacto del cliente cli-001"))
