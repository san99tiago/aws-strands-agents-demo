"""
EX-02: MODEL SELECTION IN AMAZON BEDROCK - Same agent, different LLMs.

Slide: "Selección de modelo en Amazon Bedrock"
Prerequisites:
    - Active AWS credentials (aws login / AWS_PROFILE / AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY ...)
    - Model access enabled in Amazon Bedrock (region us-east-1 in this demo).

Concepts:
    - BedrockModel(model_id=..., region_name=..., max_tokens=...)
    - Cross-region inference profiles: "us." / "global." prefixes.
    - Swap the model, keep the agent: Claude, Nova, Llama, DeepSeek, Kimi, gpt-oss... all in Bedrock.

Run:
    poetry run python local/ex_02_bedrock_models.py
"""

from strands import Agent
from strands.models import BedrockModel

QUESTION = "¿Qué es la bandeja paisa? Responde en 2 frases."

BEDROCK_MODELS = {
    "Anthropic Claude Sonnet 5.5": "us.anthropic.claude-sonnet-5-5",
    "Amazon Nova 2 Lite": "us.amazon.nova-2-lite-v1:0",
    "Meta Llama 4 Maverick": "us.meta.llama4-maverick-17b-instruct-v1:0",
    "DeepSeek V3.2": "deepseek.v3.2",
    "Moonshot Kimi K3": "us.moonshotai.kimi-k3",
}

for name, model_id in BEDROCK_MODELS.items():
    model = BedrockModel(model_id=model_id, region_name="us-east-1", max_tokens=1500)
    agent = Agent(model=model, system_prompt="Responde en español.", callback_handler=None)
    print(f"\n=== {name} ({model_id})\n{agent(QUESTION)}")
