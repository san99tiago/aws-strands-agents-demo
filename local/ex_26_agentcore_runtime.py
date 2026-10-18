"""
EX-26: DEPLOY - Same agent, production runtime with Amazon Bedrock AgentCore.

Slide: "From laptop to production: AgentCore Runtime"
Concepts:
    - BedrockAgentCoreApp: HTTP contract (/invocations, /ping) expected by AgentCore Runtime.
    - @app.entrypoint: your handler; payload in, JSON (or a stream via async generator) out.
    - Session isolation per user (microVM), up to 8h sessions, IAM / OAuth identity, OTEL observability.
    - Deploy with the AgentCore CLI (npm i -g @aws/agentcore):
          agentcore create  ->  agentcore dev  ->  agentcore deploy  ->  agentcore invoke
    - Expose it to clients through API Gateway + Lambda (never public Lambda Function URLs).

Run locally (port 8080):
    poetry run python local/ex_26_agentcore_runtime.py
    curl -s localhost:8080/invocations -H 'Content-Type: application/json' \
         -d '{"prompt": "Cuál es la tasa del CDT a 180 días?"}'
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


@tool
def get_cdt_rate(term_days: int) -> float:
    """Get AnyBank CDT annual effective rate for a term in days (30, 90, 180, 360)."""
    return {30: 9.1, 90: 10.4, 180: 11.2, 360: 11.8}.get(term_days, 0.0)


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_cdt_rate],
    system_prompt="Eres el asistente de AnyBank desplegado en AgentCore Runtime. Responde breve en español.",
    callback_handler=None,
)


@app.entrypoint
def invoke(payload: dict) -> dict:
    result = agent(payload.get("prompt", "Hola"))
    return {"answer": str(result), "stop_reason": result.stop_reason, "usage": result.metrics.accumulated_usage}


if __name__ == "__main__":
    app.run()
