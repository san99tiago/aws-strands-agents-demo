"""
EX-12: HUMAN-IN-THE-LOOP - Pause the agent, ask a human, resume.

Slide: "Human-in-the-loop"
Concepts:
    - HumanInTheLoop intervention: every tool NOT in allowed_tools needs approval.
    - Default mode = INTERRUPT/RESUME (perfect for APIs, AgentCore, web apps):
        result.stop_reason == "interrupt"  -> show result.interrupts to a human
        agent([{"interruptResponse": {"interruptId": id, "response": "y"}}]) -> resume
    - ask="stdio" -> interactive CLI prompt instead.

Run:
    poetry run python local/ex_12_human_in_the_loop.py
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.vended_interventions.hitl import HumanInTheLoop


@tool
def estado_tarjeta(ultimos4: str) -> str:
    """Consulta el estado y el cupo disponible de una tarjeta de crédito de RufusBank.

    Args:
        ultimos4: Últimos 4 dígitos de la tarjeta.
    """
    return f"Tarjeta ****{ultimos4}: ACTIVA, cupo disponible 3.200.000 COP"


@tool
def aumentar_cupo(ultimos4: str, nuevo_cupo_cop: int) -> str:
    """Aumenta el cupo de una tarjeta de crédito (requiere aprobación de un analista).

    Args:
        ultimos4: Últimos 4 dígitos de la tarjeta.
        nuevo_cupo_cop: Nuevo cupo en COP.
    """
    return f"Cupo de ****{ultimos4} actualizado a {nuevo_cupo_cop:,} COP"


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[estado_tarjeta, aumentar_cupo],
    interventions=[HumanInTheLoop(allowed_tools=["estado_tarjeta"])],  # read-only = auto-approved
    system_prompt="Eres el agente de tarjetas de RufusBank. Responde breve en español.",
    callback_handler=None,
)

result = agent("Revisa mi tarjeta 4321 y súbeme el cupo a 8 millones")

while result.stop_reason == "interrupt":
    responses = []
    for interrupt in result.interrupts:
        print(f"\n\033[93m[APROBACIÓN REQUERIDA]\033[0m {interrupt.name}: {interrupt.reason}")
        answer = input("Analista, ¿apruebas? (y/n): ").strip() or "y"
        responses.append({"interruptResponse": {"interruptId": interrupt.id, "response": answer}})
    result = agent(responses)  # resume exactly where it paused

print("\nAGENT>", str(result).strip())
