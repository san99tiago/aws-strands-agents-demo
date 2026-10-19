"""
EX-16: MODEL ROUTING - The right model for each request (cost + quality).

Slide: "ModelRouter"
Concepts:
    - ModelRouter([candidates], strategy=...) is itself a Model -> Agent(model=router).
    - ClassifierStrategy(model=fast): a small, fast LLM picks the LEAST capable model that can do the job.
    - 3 tiers, 2 providers (all in Amazon Bedrock):
        fast      -> Claude Haiku   | OpenAI GPT Luna   : greetings, simple FAQs
        balanced  -> Claude Sonnet  | OpenAI GPT Terra  : product explanations, simple calculations
        capable   -> Claude Opus    | OpenAI GPT Sol    : complex multi-step financial analysis
    - FallbackStrategy (default): if a model fails/throttles, switch to the next one (resilience).

Run:
    poetry run python local/ex_16_model_router.py                    # Claude (Anthropic)
    PROVIDER=openai poetry run python local/ex_16_model_router.py    # OpenAI GPTs
"""

import logging
import os

from strands import Agent
from strands.models import BedrockModel, ClassifierStrategy, ModelRouter, RoutingCandidate

TIERS = {  # tier: (Anthropic Claude, OpenAI GPT)
    "fast": ("us.anthropic.claude-haiku-5-5", "us.openai.gpt-6-luna"),
    "balanced": ("us.anthropic.claude-sonnet-5-5", "us.openai.gpt-5.6-terra"),
    "capable": ("us.anthropic.claude-opus-5-5", "us.openai.gpt-6.1-sol"),
}
idx = 1 if os.getenv("PROVIDER", "anthropic").lower() == "openai" else 0
fast, balanced, capable = (BedrockModel(model_id=TIERS[t][idx], region_name="us-east-1", max_tokens=4000) for t in TIERS)

router = ModelRouter(
    [
        RoutingCandidate(fast, name=TIERS["fast"][idx], description="Fastest and cheapest. Greetings, simple FAQs."),
        RoutingCandidate(balanced, name=TIERS["balanced"][idx], description="Balanced. Product explanations, simple calculations."),
        RoutingCandidate(capable, name=TIERS["capable"][idx], description="Most capable. Complex multi-step financial analysis."),
    ],
    strategy=ClassifierStrategy(model=fast),
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
