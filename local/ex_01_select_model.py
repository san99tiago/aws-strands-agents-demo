from strands import Agent
from strands.models import BedrockModel

bedrock_model1 = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    params={"max_tokens": 1600, "temperature": 0.7},
)
bedrock_model2 = BedrockModel(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

agent = Agent(model=bedrock_model2)
response = agent("Qué es el 4x1000?")
