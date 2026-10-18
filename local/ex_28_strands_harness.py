"""
EX-28: STRANDS HARNESS - A batteries-included agent in ONE call.

Slide: "SDK vs Harness: build your loop or start from a complete one"
Concepts:
    - strands-harness (Sep-2026): create_harness(...) returns a regular strands.Agent, pre-wired with
      the best practices you saw in ex_01..ex_27:
        * built-in tools: shell, read, write, edit, web_fetch, web_search, subagent, programmatic_tool_caller
        * plugins: todos (planning), environment (cwd/OS awareness)
        * sessions, long-term memory, skills, context management (auto compaction), prompt caching
        * interventions: "ask" (approve every risky tool) | "smart" | policy text | .cedar file
        * effort: off | minimal | low | medium | high | xhigh | max | auto (extended thinking)
    - Enable ONLY the tools you need (least privilege) with builtin_tools={...}.

Run:
    poetry run python local/ex_28_strands_harness.py
"""

import os

from strands import tool
from strands_harness import create_harness

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "transactions_oct_2026.csv")


@tool
def get_customer_profile(customer_id: str) -> dict:
    """Get the KYC profile of an AnyBank customer."""
    return {"customer_id": customer_id, "name": "Laura", "segment": "preferente", "card_last4": "4321", "country": "CO"}


agent = create_harness(
    model="bedrock/us.anthropic.claude-sonnet-5-5",
    effort="low",
    instructions=(
        "Eres un analista de fraude y finanzas personales de AnyBank. Responde en español. "
        "Trabaja SOLO con los archivos que te indiquen."
    ),
    tools=[get_customer_profile],
    builtin_tools={"*": False, "read": True, "write": True},  # least privilege: no shell, no web
    skills=os.path.join(HERE, "skills"),
    session={"id": "anybank-harness-demo", "dir": os.path.join(HERE, ".agent", "sessions")},
    memory=False,
    callback_handler=None,
)

result = agent(
    f"Lee {DATA}. 1) Resume los gastos de octubre por categoría. 2) Detecta transacciones sospechosas "
    f"de cust-001 y aplica el skill de fraude. 3) Guarda un reporte markdown en {os.path.join(HERE, '.agent', 'report_cust001.md')}."
)
print(str(result).strip())
print("\nTools used:", list(agent.event_loop_metrics.tool_metrics.keys()))
