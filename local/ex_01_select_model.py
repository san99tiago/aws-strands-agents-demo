"""
EX-01: SELECT THE MODEL - Model-agnostic by design.

Slide: "Model Providers: same agent, any LLM"
Concepts:
    - BedrockModel(model_id=..., temperature=..., max_tokens=...)
    - Cross-region inference profiles: "us." / "global." prefixes.
    - Same Agent code works with Claude, Amazon Nova, Llama, OpenAI, Ollama, LiteLLM...
    - Compare quality, latency and tokens for the SAME question.

Run:
    poetry run python local/ex_01_select_model.py
"""

import time

from strands import Agent
from strands.models import BedrockModel

REGION = "us-east-1"
QUESTION = "Explica en 2 frases qué es una tarjeta de crédito para un cliente nuevo de AnyBank."

MODELS = {
    "Claude Sonnet 5.5 (balanced)": BedrockModel(
        model_id="us.anthropic.claude-sonnet-5-5", region_name=REGION, max_tokens=400
    ),
    "Claude Haiku 5.5 (fast/cheap)": BedrockModel(
        model_id="us.anthropic.claude-haiku-5-5", region_name=REGION, max_tokens=400
    ),
    "Amazon Nova 2 Lite (low cost)": BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name=REGION,
        max_tokens=400,
        temperature=0.3,
    ),
}

# Other providers (same Agent API, just swap the model object):
#   from strands.models.anthropic import AnthropicModel    -> pip install 'strands-agents[anthropic]'
#   from strands.models.openai import OpenAIModel          -> pip install 'strands-agents[openai]'
#   from strands.models.ollama import OllamaModel          -> pip install 'strands-agents[ollama]'
#   from strands.models.litellm import LiteLLMModel        -> pip install 'strands-agents[litellm]'

for name, model in MODELS.items():
    agent = Agent(
        model=model,
        system_prompt="Eres un asesor de AnyBank. Responde en español, claro y breve.",
        callback_handler=None,  # silence streaming, we print at the end
    )
    start = time.perf_counter()
    result = agent(QUESTION)
    elapsed = time.perf_counter() - start
    usage = result.metrics.accumulated_usage
    print(f"\n=== {name} | {elapsed:.1f}s | in={usage['inputTokens']} out={usage['outputTokens']}")
    print(str(result).strip())
