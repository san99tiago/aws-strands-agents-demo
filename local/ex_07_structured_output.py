"""
EX-07: STRUCTURED OUTPUT - Agents that return structured data (Pydantic), not prose.

Slide: "Agentes que devuelven datos estructurados"
Concepts:
    - agent(prompt, structured_output_model=MyModel) -> result.structured_output (typed object).
    - The SDK validates with Pydantic and auto-retries on validation errors.
    - Messy text (email, chat, transcript) -> clean JSON for your core systems / APIs.

Run:
    poetry run python local/ex_07_structured_output.py
"""

from typing import Literal

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel


class SolicitudCredito(BaseModel):
    """Solicitud de crédito extraída del mensaje de un cliente."""

    nombre_completo: str
    ingreso_mensual_cop: int
    monto_solicitado_cop: int
    plazo_meses: int
    tipo: Literal["vivienda", "vehiculo", "flying_vehicle", "educacion", "libre_inversion"]
    alertas_riesgo: list[str] = Field(description="Alertas de riesgo para el analista")


MENSAJE = """
*burp* Hola RufusBank, soy Rick Sanchez, científico, 70 años. Gano como 1 millón al mes (a veces más,
a veces me pagan en cristales interdimensionales). Necesito 50.000.000 para un vehículo volador nuevo,
el otro lo choqué en otra dimensión. Págalo en 36 meses. Mi trabajo es... peligroso. Muy peligroso.
"""

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    system_prompt="Eres analista de originación de crédito de RufusBank.",
    callback_handler=None,
)

result = agent(f"Extrae la solicitud de crédito:\n{MENSAJE}", structured_output_model=SolicitudCredito)
print(result.structured_output.model_dump_json(indent=2))
