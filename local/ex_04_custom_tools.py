"""
EX-04: CUSTOM TOOLS - Turn any Python function into a tool with @tool.

Slide: "@tool: herramientas propias"
Concepts:
    - Docstring = tool description (the LLM reads it to decide WHEN to use the tool).
    - Type hints + Args = input JSON schema.
    - Mock RufusBank "core banking" data (swap it for DynamoDB / APIs in real life).

Run:
    poetry run python local/ex_04_custom_tools.py
"""

from strands import Agent, tool
from strands.models import BedrockModel

CUENTAS = {"cli-001": {"nombre": "Laura", "ahorros_cop": 4_250_000, "deuda_tarjeta_cop": 1_180_000}}


@tool
def consultar_saldo(cliente_id: str) -> dict:
    """Consulta el saldo de ahorros y la deuda de la tarjeta de crédito (en COP) de un cliente de RufusBank.

    Args:
        cliente_id: Identificador del cliente, por ejemplo "cli-001".
    """
    return CUENTAS.get(cliente_id, {"error": f"Cliente {cliente_id} no encontrado"})


@tool
def simular_credito(monto_cop: int, plazo_meses: int, tasa_mensual: float = 0.015) -> dict:
    """Simula la cuota mensual fija de un crédito de libre inversión de RufusBank.

    Args:
        monto_cop: Monto solicitado en COP.
        plazo_meses: Plazo del crédito en meses.
        tasa_mensual: Tasa de interés mensual (0.015 = 1,5% M.V.).
    """
    cuota = monto_cop * tasa_mensual / (1 - (1 + tasa_mensual) ** -plazo_meses)
    return {"cuota_mensual_cop": round(cuota), "total_pagado_cop": round(cuota * plazo_meses)}


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[consultar_saldo, simular_credito],
    system_prompt="Eres el asistente virtual de RufusBank. El cliente autenticado es cli-001. Responde en español.",
)

agent("¿Cuánta plata tengo? Y si pido 10 millones a 24 meses, ¿de cuánto sería la cuota?")
