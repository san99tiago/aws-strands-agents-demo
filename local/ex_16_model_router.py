"""
EX-16: MODEL ROUTING - The right Claude for each request (cost + quality).

Slide: "ModelRouter"
Concepts:
    - ModelRouter([candidates], strategy=...) is itself a Model -> Agent(model=router).
    - ClassifierStrategy(model=haiku): a small, fast LLM picks the LEAST capable model that can do the job:
        Haiku  -> greetings, simple FAQs
        Sonnet -> product explanations, simple calculations
        Opus   -> complex multi-step financial analysis
    - FallbackStrategy (default): if a model fails/throttles, switch to the next one (resilience).

Run:
    poetry run python local/ex_16_model_router.py
"""

import logging

from strands import Agent
from strands.models import BedrockModel, ClassifierStrategy, ModelRouter, RoutingCandidate

REGION = "us-east-1"
haiku = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name=REGION, max_tokens=800)
sonnet = BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name=REGION, max_tokens=2000)
opus = BedrockModel(model_id="us.anthropic.claude-opus-5-5", region_name=REGION, max_tokens=4000)

router = ModelRouter(
    [
        RoutingCandidate(haiku, name="claude-haiku", description="Fastest and cheapest. Greetings, simple FAQs."),
        RoutingCandidate(sonnet, name="claude-sonnet", description="Balanced. Product explanations, simple calculations."),
        RoutingCandidate(opus, name="claude-opus", description="Most capable. Complex multi-step financial analysis."),
    ],
    strategy=ClassifierStrategy(model=haiku),
)


class ShowChoice(logging.Handler):  # print the router decision ("candidate selected" log line)
    def emit(self, record: logging.LogRecord) -> None:
        if "candidate selected" in record.getMessage():
            print("   [router]", record.getMessage().split(" | ")[0])


logging.getLogger("strands.models.routing.router").setLevel(logging.INFO)
logging.getLogger("strands.models.routing.router").addHandler(ShowChoice())

agent = Agent(model=router, system_prompt="Eres el asistente de RufusBank. Responde en español, máximo 8 líneas.",
              callback_handler=None)

for q in [
    "¡Hola! ¿A qué hora abren las oficinas?",
    "¿Qué diferencia hay entre una tarjeta débito y una de crédito?",
    "Gano 7 millones y tengo 3 deudas (tarjeta 26% EA 5M, libre inversión 19% EA 12M, carro 14% EA 30M); puedo "
    "pagar 2,5M al mes. Compara avalancha vs bola de nieve y dime cuál me ahorra más intereses.",
]:
    print(f"\nQ: {q[:80]}...")
    print(f"A: {str(agent(q)).strip()[:280]}...")
