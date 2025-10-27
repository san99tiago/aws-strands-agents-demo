import requests
from strands import Agent, tool
from strands.models import BedrockModel


@tool
def get_datafonos_status(store_id: str) -> str:
    """Get the status of RufusBank datafonos from the API."""
    response = requests.get(
        f"https://os3kf6cbk0.execute-api.us-east-1.amazonaws.com/prod/api/v1/datafonos?store_id={store_id}"
    )
    return response.json()


bedrock_model = BedrockModel(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
agent = Agent(tools=[get_datafonos_status], model=bedrock_model)
print(
    agent("Dime el status de los datáfonos virtuales de la tienda <salpicones-3-2-1>?")
)
