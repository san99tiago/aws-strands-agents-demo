"""
EX-04: CUSTOM TOOLS - Turn any Python function into a tool with @tool.

Slide: "@tool: your business logic, agent-ready"
Concepts:
    - Docstring = tool description (what the LLM reads to decide).
    - Type hints = JSON schema for the input.
    - ToolContext: access agent state / tool_use metadata inside a tool.
    - Mock "core banking" data (swap for DynamoDB / APIs in real life).

Run:
    poetry run python local/ex_04_custom_tool.py
"""

from strands import Agent, ToolContext, tool
from strands.models import BedrockModel

# Mock core-banking data (generic FSI demo)
ACCOUNTS = {
    "cust-001": {"name": "Laura", "savings": 4_250_000, "credit_card_debt": 1_180_000},
    "cust-002": {"name": "Andrés", "savings": 820_000, "credit_card_debt": 0},
}
TRANSACTIONS = {
    "cust-001": [
        {"date": "2026-10-01", "merchant": "Supermercado", "amount": -185_000},
        {"date": "2026-10-03", "merchant": "Nómina", "amount": 3_900_000},
        {"date": "2026-10-09", "merchant": "Streaming", "amount": -39_900},
        {"date": "2026-10-12", "merchant": "Restaurante", "amount": -142_000},
    ],
}


@tool
def get_balance(customer_id: str) -> dict:
    """Get the savings balance and credit card debt (in COP) of an AnyBank customer.

    Args:
        customer_id: The customer identifier, e.g. "cust-001".
    """
    account = ACCOUNTS.get(customer_id)
    if not account:
        return {"status": "error", "content": [{"text": f"Customer {customer_id} not found"}]}
    return {"status": "success", "content": [{"json": account}]}


@tool
def get_transactions(customer_id: str, limit: int = 10) -> list[dict]:
    """List the most recent transactions of an AnyBank customer.

    Args:
        customer_id: The customer identifier.
        limit: Maximum number of transactions to return.
    """
    return TRANSACTIONS.get(customer_id, [])[:limit]


@tool(context=True)
def remember_preference(preference: str, tool_context: ToolContext) -> str:
    """Remember a customer preference for the rest of the conversation.

    Args:
        preference: The preference to remember (e.g. "prefiere respuestas cortas").
    """
    prefs = tool_context.agent.state.get("preferences") or []
    prefs.append(preference)
    tool_context.agent.state.set("preferences", prefs)
    return f"Preferencia guardada ({len(prefs)} en total)."


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[get_balance, get_transactions, remember_preference],
    system_prompt="Eres el asistente virtual de AnyBank. El cliente autenticado es cust-001. Responde en español.",
)

agent("Cuánta plata tengo y cuánto debo en la tarjeta?")
print("\n" + "-" * 60)
agent("Cuáles fueron mis gastos de este mes? Ah, y recuerda que prefiero respuestas en viñetas.")
print("\n\nAgent state ->", agent.state.get())
