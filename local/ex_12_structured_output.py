"""
EX-12: STRUCTURED OUTPUT - From free text to validated Pydantic objects.

Slide: "Structured Output: agents that return DATA, not prose"
Concepts:
    - Agent(structured_output_model=MyModel) or agent(prompt, structured_output_model=MyModel).
    - The SDK registers a hidden tool + validates with Pydantic (auto-retries on validation errors).
    - result.structured_output -> typed object, ready for your core systems / APIs.

Run:
    poetry run python local/ex_12_structured_output.py
"""

from typing import Literal

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel


class CreditApplication(BaseModel):
    """A credit application extracted from a customer message."""

    full_name: str
    monthly_income_cop: int = Field(description="Monthly income in COP")
    requested_amount_cop: int
    term_months: int
    purpose: Literal["vivienda", "vehiculo", "educacion", "libre_inversion", "otro"]
    employment_type: Literal["empleado", "independiente", "pensionado", "desconocido"]
    risk_flags: list[str] = Field(default_factory=list, description="Potential risks for an analyst")


EMAIL = """
Buenas tardes, mi nombre es Carolina Restrepo, soy independiente (diseñadora) y gano alrededor de
6 millones y medio al mes, aunque varía. Quiero pedir un préstamo de 45 millones para comprar
un carro usado y pagarlo en 5 años. Ya tengo otro crédito de libranza vigente.
"""

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    system_prompt="Eres un analista de originación de crédito de AnyBank.",
    callback_handler=None,
)

result = agent(f"Extrae la solicitud de crédito:\n{EMAIL}", structured_output_model=CreditApplication)
app: CreditApplication = result.structured_output

print(app.model_dump_json(indent=2))
print(f"\nDebt-to-income check: cuota aprox / ingreso = "
      f"{(app.requested_amount_cop / app.term_months) / app.monthly_income_cop:.0%}")
