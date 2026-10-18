"""
EX-24: MODEL ROUTING - Right model for each request (cost + resilience).

Slide: "ModelRouter: fallback & classifier strategies"
Concepts:
    - ModelRouter([candidates], strategy=...) is itself a Model -> Agent(model=router).
    - FallbackStrategy (default): if a model fails/throttles, switch to the next one (resilience).
    - ClassifierStrategy(model=cheap): a small LLM picks the LEAST capable model that can do the job
      -> simple FAQs go to Haiku/Nova, complex analysis to Sonnet (cost optimization).
    - API is provisional (may change).

Run:
    poetry run python local/ex_24_model_router.py
"""

import logging

from strands import Agent
from strands.models import BedrockModel, ClassifierStrategy, ModelRouter, RoutingCandidate

REGION = "us-east-1"
nova = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", region_name=REGION, max_tokens=600)
haiku = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name=REGION, max_tokens=600)
sonnet = BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name=REGION, max_tokens=4000)

router = ModelRouter(
    [
        RoutingCandidate(nova, name="nova-2-lite", description="Cheapest. Greetings, simple FAQs, short answers."),
        RoutingCandidate(haiku, name="haiku-5-5", description="Fast. Product explanations, simple calculations."),
        RoutingCandidate(sonnet, name="sonnet-5-5", description="Most capable. Multi-step financial analysis, planning."),
    ],
    strategy=ClassifierStrategy(model=nova),
)

# Print the router decision (the router logs "candidate selected" at INFO level)
class _ShowChoice(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if "candidate selected" in record.getMessage():
            print("   [router]", record.getMessage().split(" | ")[0])


router_logger = logging.getLogger("strands.models.routing.router")
router_logger.setLevel(logging.INFO)
router_logger.addHandler(_ShowChoice())

agent = Agent(
    model=router,
    system_prompt="Eres el asistente de AnyBank. Responde en español, máximo 10 líneas.",
    callback_handler=None,
)

for q in [
    "Hola! a qué hora abren las oficinas?",
    "Gano 7 millones, tengo 3 deudas (tarjeta 26% EA 5M, libre inversión 19% EA 12M, carro 14% EA 30M) y "
    "puedo pagar 2,5M al mes. Diseña una estrategia avalancha vs bola de nieve y dime cuál me ahorra más intereses.",
]:
    print(f"\nQ: {q[:90]}...")
    result = agent(q)
    print(f"A: {str(result).strip()[:300]}...")
    print(f"   tokens={result.metrics.accumulated_usage['totalTokens']}")
