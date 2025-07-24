import os
import random
from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

# Specify custom OTLP endpoint -- Important to setup for DEMO!
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4320"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = "name=santi,cost=awsdemos"

# Setup Strands OTEL config
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()  # Send traces to OTLP endpoint
strands_telemetry.setup_console_exporter()  # Print traces to console
strands_telemetry.setup_meter(
    enable_console_exporter=False, enable_otlp_exporter=True
)  # Setup new meter provider and sets it as global

bedrock_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    params={"max_tokens": 1600, "temperature": 0.7},
)


@tool
def get_balance(user_id: str) -> str:
    """Get balance of a RufusBank user.
    :param user_id (str): RufusBank user ID.
    """
    saldo = random.randint(1000, 100000)
    return f"El saldo del usuario {user_id} es de: {saldo} COP..."


@tool
def reset_credit_card(user_id: str) -> str:
    """Reset credit card of a RufusBank user.
    :param user_id (str): RufusBank user ID.
    """
    return f"La tarjeta del usuario {user_id} fue reseteada correctamente..."


agent = Agent(model=bedrock_model, tools=[get_balance, reset_credit_card])
print(agent("(user_id: santi123) Cuánta plata tengo en mi cuenta?"))
# print(agent("(user_id: santi123) Me ayudas restaurando mi tarjeta porfa?"))
print(agent("(user_id: santi123) Me restauras mi tarjeta y me cuentas mi saldo?"))
