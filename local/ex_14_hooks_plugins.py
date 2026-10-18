"""
EX-14: HOOKS & PLUGINS - Extend the agent loop without touching the agent.

Slide: "Hooks: lifecycle events you can observe and modify"
Concepts:
    - Lifecycle events: BeforeInvocation, BeforeModelCall, AfterModelCall, BeforeToolCall,
      AfterToolCall, AfterInvocation, MessageAdded...
    - agent.add_hook(callback, EventType) for quick wiring.
    - Plugin: a reusable bundle of @hook methods (+ optional @tool) -> Agent(plugins=[...]).
    - Typical uses: audit logs (compliance), PII masking, cost tracking, rate limiting.

Run:
    poetry run python local/ex_14_hooks_plugins.py
"""

import re
import time

from strands import Agent, tool
from strands.hooks import AfterInvocationEvent, AfterToolCallEvent, BeforeToolCallEvent
from strands.models import BedrockModel
from strands.plugins import Plugin, hook


@tool
def get_customer_contact(customer_id: str) -> str:
    """Get the contact data of a customer.

    Args:
        customer_id: Customer identifier.
    """
    return f"Cliente {customer_id}: email laura.gomez@mail.com, celular 3001234567, cédula 1037654321"


class ComplianceAuditPlugin(Plugin):
    """Audit every tool call (who/what/when/how long) and mask PII in tool results."""

    name = "anybank-compliance-audit"

    def __init__(self) -> None:
        super().__init__()
        self.audit_log: list[dict] = []
        self._started: dict[str, float] = {}

    @hook
    def before_tool(self, event: BeforeToolCallEvent) -> None:
        self._started[event.tool_use["toolUseId"]] = time.perf_counter()
        print(f"\n[AUDIT] -> {event.tool_use['name']} input={event.tool_use['input']}")

    @hook
    def after_tool(self, event: AfterToolCallEvent) -> None:
        elapsed = time.perf_counter() - self._started.pop(event.tool_use["toolUseId"], time.perf_counter())
        # Mask PII BEFORE the result goes back to the model (and to the logs)
        for block in event.result["content"]:
            if "text" in block:
                text = re.sub(r"[\w.]+@[\w.]+", "***@***", block["text"])
                block["text"] = re.sub(r"\b\d{7,10}\b", "**********", text)
        self.audit_log.append({"tool": event.tool_use["name"], "ms": round(elapsed * 1000, 2)})
        print(f"[AUDIT] <- {event.tool_use['name']} masked_result={event.result['content']}")


audit = ComplianceAuditPlugin()
agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_customer_contact],
    plugins=[audit],
    system_prompt="Eres un agente de back-office de AnyBank. Responde en español.",
)

# Quick hook without a plugin class:
agent.add_hook(lambda e: print(f"\n[COST] tokens={e.agent.event_loop_metrics.accumulated_usage['totalTokens']}"),
               AfterInvocationEvent)

agent("Dame los datos de contacto del cliente cust-001")
print("\nAudit log:", audit.audit_log)
