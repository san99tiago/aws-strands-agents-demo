"""
EX-08: CALL YOUR APIs - Wrap REST APIs (e.g. API Gateway + Lambda) as tools.

Slide: "Agents on top of your existing APIs"
Concepts:
    - A @tool is just Python: call requests/httpx/boto3, validate, return JSON.
    - Return {"status": "error", ...} so the model can recover gracefully.
    - Timeouts are a MUST for production tools.

Set your API:
    export ANYBANK_API_URL="https://<api-id>.execute-api.us-east-1.amazonaws.com/prod"

Run:
    poetry run python local/ex_08_apis.py
"""

import os

import requests
from strands import Agent, tool
from strands.models import BedrockModel

API_URL = os.getenv("ANYBANK_API_URL", "https://os3kf6cbk0.execute-api.us-east-1.amazonaws.com/prod")


@tool
def get_pos_terminals_status(store_id: str) -> dict:
    """Get the status of the POS terminals (datáfonos) of a merchant store.

    Args:
        store_id: The merchant store identifier, e.g. "salpicones-3-2-1".
    """
    try:
        response = requests.get(f"{API_URL}/api/v1/datafonos", params={"store_id": store_id}, timeout=10)
        response.raise_for_status()
        # Bedrock requires a JSON *object* in toolResult (lists must be wrapped)
        return {"status": "success", "content": [{"json": {"store_id": store_id, "data": response.json()}}]}
    except requests.RequestException as error:
        return {"status": "error", "content": [{"text": f"API error: {error}"}]}


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_pos_terminals_status],
    system_prompt="Eres el asistente para comercios de AnyBank. Responde en español con una tabla resumen.",
)
agent("Dime el estado de los datáfonos de la tienda salpicones-3-2-1")
