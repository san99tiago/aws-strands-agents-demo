"""
EX-17: STEERING - Just-in-time guidance instead of a giant system prompt.

Slide: "Steering: progressive disclosure of rules"
Concepts:
    - LLMSteeringHandler(system_prompt=...) is a PLUGIN: before each tool call, a (cheap) judge LLM
      reviews the action in context and decides: proceed | guide | interrupt.
    - Keeps the main prompt small; rules are evaluated only when they matter.
    - LedgerProvider: context provider that tracks tool history so the judge sees the trajectory.
    - Compare with ex_15: Interventions = deterministic code rules, Steering = semantic LLM rules.

Run:
    poetry run python local/ex_17_steering.py
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands.vended_plugins.steering import LLMSteeringHandler


@tool
def send_customer_message(customer_id: str, channel: str, message: str) -> str:
    """Send a message to a customer.

    Args:
        customer_id: Customer identifier.
        channel: sms | email | whatsapp
        message: The message text.
    """
    return f"Mensaje enviado a {customer_id} por {channel}."


tone_steering = LLMSteeringHandler(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    system_prompt="""
    You review outbound messages of a collections (cobranza) agent of a bank. Guidelines (Colombian regulation
    and AnyBank policy):
      - Messages must be respectful, never threatening, never mention legal action or reporting to credit bureaus
        unless the customer is > 90 days late.
      - SMS max 160 characters. Must include the official line #888.
      - Never include full account numbers.
    If the message violates a guideline, return 'guide' with precise feedback to rewrite it. Otherwise 'proceed'.
    """,
)

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[send_customer_message],
    plugins=[tone_steering],
    system_prompt="Eres un agente de cobranza de AnyBank. Sé directo y presiona para que paguen.",
    callback_handler=None,
)

result = agent(
    "El cliente cust-777 tiene 12 días de mora en la cuenta 4556-7788-9900. Mándale un SMS fuerte "
    "diciéndole que lo vamos a reportar a centrales de riesgo si no paga hoy."
)
print("AGENT>", str(result).strip())
print("\nFinal SMS sent:")
for m in agent.messages:
    for block in m["content"]:
        if "toolUse" in block:
            print(" ->", block["toolUse"]["input"])
