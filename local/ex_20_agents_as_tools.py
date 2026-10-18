"""
EX-20: MULTI-AGENT (1/4) - Agents as Tools (supervisor + specialists).

Slide: "Agents as Tools: hierarchical delegation"
Concepts:
    - agent.as_tool(): any Agent becomes a tool of another agent (or pass the Agent directly in tools=[]).
    - The SUPERVISOR decides which specialist(s) to call; each specialist has its own prompt/tools/model.
    - delegate=True -> the specialist's answer is returned directly (saves one model call).
    - Use cheaper models for specialists, a stronger one for orchestration.

Run:
    poetry run python local/ex_20_agents_as_tools.py
"""

from strands import Agent, tool
from strands.models import BedrockModel

fast = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")
smart = BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1")


@tool
def get_portfolio(customer_id: str) -> dict:
    """Get the investment portfolio of a customer (COP)."""
    return {"CDT": 20_000_000, "Fondo renta fija": 8_000_000, "Acciones locales": 4_000_000}


@tool
def get_credit_products(customer_id: str) -> dict:
    """Get the active credit products of a customer."""
    return {"Tarjeta de crédito": {"cupo": 6_000_000, "usado": 4_800_000, "tasa_ea": 26.4}}


investments_agent = Agent(
    name="investments_advisor",
    description="Specialist in the customer's investments: portfolio, risk profile and diversification.",
    model=fast,
    tools=[get_portfolio],
    system_prompt="Eres especialista en inversiones de AnyBank. Responde en 3 viñetas.",
    callback_handler=None,
)
credit_agent = Agent(
    name="credit_advisor",
    description="Specialist in the customer's loans and credit cards: debt, rates and payment strategies.",
    model=fast,
    tools=[get_credit_products],
    system_prompt="Eres especialista en crédito de AnyBank. Responde en 3 viñetas.",
    callback_handler=None,
)

supervisor = Agent(
    model=smart,
    tools=[investments_agent.as_tool(), credit_agent.as_tool()],
    system_prompt=(
        "Eres el banquero personal (supervisor) de AnyBank. Delega en los especialistas y luego entrega "
        "UNA recomendación integrada y breve en español. Cliente: cust-001."
    ),
)

supervisor("Tengo plata invertida pero también deuda en la tarjeta. Qué me conviene hacer este mes?")
print("\n\nSpecialists called:", list(supervisor.event_loop_metrics.tool_metrics.keys()))
