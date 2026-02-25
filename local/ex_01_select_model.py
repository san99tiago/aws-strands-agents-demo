import random
from strands import Agent
from strands.models import BedrockModel

bedrock_model1 = BedrockModel(
    model_id="us.amazon.nova-2-lite-v1:0",
    # model_id="amazon.nova-lite-v1:0",
    # model_id="amazon.nova-pro-v1:0",
    # params={"max_tokens": 1600, "temperature": 0.7},
)
bedrock_model2 = BedrockModel(model="global.anthropic.claude-sonnet-4-5-20250929-v1:0")
bedrock_model3 = BedrockModel(model="anthropic.claude-opus-4-1-20250805-v1:0")
bedrock_model4 = BedrockModel(model="meta.llama4-maverick-17b-instruct-v1:0")

# print("\n---------------------------\n")
agent = Agent(model=bedrock_model1)

for i in range(5):
    question = f"Hola, en Colombia cuánto es el impuesto predial de de {random.randint(1000, 10000)}?"
    response = agent(question)
    print(f"\n-----------\nResponse {i+1}: {response}")
