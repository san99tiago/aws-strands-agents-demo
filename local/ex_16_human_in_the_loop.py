"""
EX-16: HUMAN-IN-THE-LOOP - Pause the agent, ask a human, resume.

Slide: "Interrupts: stateless approval flows"
Concepts:
    - HumanInTheLoop intervention: every tool NOT in allowed_tools needs approval.
    - Default mode = INTERRUPT/RESUME (perfect for APIs, AgentCore, web apps):
        result.stop_reason == "interrupt"  -> show result.interrupts to a human
        agent([{"interruptResponse": {"interruptId": id, "response": "y"}}]) -> resume
    - ask="stdio" -> interactive CLI prompt instead.
    - Also available: handoff_to_user vended tool, Confirm() decision in your own handlers.

Run:
    poetry run python local/ex_16_human_in_the_loop.py
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.vended_interventions.hitl import HumanInTheLoop


@tool
def get_card_status(card_last4: str) -> str:
    """Get the status of a credit card.

    Args:
        card_last4: Last 4 digits of the card.
    """
    return f"Tarjeta ****{card_last4}: ACTIVA, cupo disponible 3.200.000 COP"


@tool
def increase_credit_limit(card_last4: str, new_limit_cop: int) -> str:
    """Increase the credit limit of a card (requires analyst approval).

    Args:
        card_last4: Last 4 digits of the card.
        new_limit_cop: New credit limit in COP.
    """
    return f"Cupo de ****{card_last4} actualizado a {new_limit_cop:,} COP"


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_card_status, increase_credit_limit],
    interventions=[HumanInTheLoop(allowed_tools=["get_card_status"])],  # read-only = auto-approved
    system_prompt="Eres el agente de tarjetas de AnyBank. Responde breve en español.",
    callback_handler=None,
)

result = agent("Revisa mi tarjeta 4321 y súbeme el cupo a 8 millones")

while result.stop_reason == "interrupt":
    responses = []
    for interrupt in result.interrupts:
        print(f"\n\033[93m[APPROVAL NEEDED]\033[0m {interrupt.name}: {interrupt.reason}")
        answer = input("Analista, ¿apruebas? (y/n): ").strip() or "y"
        responses.append({"interruptResponse": {"interruptId": interrupt.id, "response": answer}})
    result = agent(responses)  # resume exactly where it paused

print("\nAGENT>", str(result).strip())
