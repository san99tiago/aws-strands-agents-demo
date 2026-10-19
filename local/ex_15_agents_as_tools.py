"""
EX-15: AGENTS AS TOOLS - A supervisor agent + 4 specialist agents.

Slide: "Agents as Tools"
Concepts:
    - agent.as_tool(): any Agent becomes a tool of another agent (hierarchical delegation).
    - The SUPERVISOR reads each specialist's name + description and decides who to call.
    - Each specialist has its own prompt and tools. Here everything runs on Claude Haiku (fast + cheap).

Run:
    poetry run python local/ex_15_agents_as_tools.py
"""

from strands import Agent, tool
from strands.models import BedrockModel

haiku = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")


@tool
def bloquear_tarjeta(ultimos4: str) -> str:
    """Bloquea de inmediato una tarjeta de RufusBank.

    Args:
        ultimos4: Últimos 4 dígitos de la tarjeta.
    """
    return f"Tarjeta ****{ultimos4} BLOQUEADA. Caso FR-20261018-0042"


@tool
def simular_credito(monto_cop: int, plazo_meses: int) -> str:
    """Simula la cuota mensual de un crédito de libre inversión (1,5% M.V.).

    Args:
        monto_cop: Monto en COP.
        plazo_meses: Plazo en meses.
    """
    return f"Cuota aprox: {monto_cop * 0.015 / (1 - 1.015 ** -plazo_meses):,.0f} COP/mes"


@tool
def crear_ticket_humano(resumen: str) -> str:
    """Crea un ticket para que un asesor humano contacte al cliente.

    Args:
        resumen: Resumen del caso para el asesor.
    """
    return "Ticket HUM-7781 creado. Un asesor te contactará en menos de 2 horas."


def especialista(name: str, description: str, prompt: str, tools: list | None = None) -> Agent:
    return Agent(name=name, description=description, model=haiku, tools=tools or [],
                 system_prompt=f"{prompt} Responde en español, máximo 3 líneas.", callback_handler=None)


faqs = especialista("faqs", "Preguntas frecuentes: horarios, oficinas, productos.", "Eres experto en FAQs de RufusBank.")
fraudes = especialista("fraudes", "Fraudes, cobros no reconocidos, robo de tarjeta.", "Eres analista antifraude.", [bloquear_tarjeta])
creditos = especialista("creditos", "Créditos y simulaciones de cuotas.", "Eres asesor de crédito.", [simular_credito])
humano = especialista("humano", "Cuando el cliente pide un humano o hay una queja.", "Escalas casos a humanos.", [crear_ticket_humano])

supervisor = Agent(
    model=haiku,  # fast + cheap supervisor; switch to sonnet for harder orchestration
    tools=[faqs.as_tool(), fraudes.as_tool(), creditos.as_tool(), humano.as_tool()],
    system_prompt="Eres el supervisor de RufusBank. Delega en los especialistas y entrega UNA respuesta breve en español.",
)

supervisor("Me robaron la tarjeta que termina en 4321, ¡bloquéala! Y de paso, ¿cuánto pagaría por 10 millones a 24 meses?")
print("\n\nSpecialists called:", list(supervisor.event_loop_metrics.tool_metrics))
