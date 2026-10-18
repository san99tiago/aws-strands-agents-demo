"""
EX-23: MULTI-AGENT (4/4) - A2A (Agent-to-Agent protocol): agents across teams/clouds/frameworks.

Slide: "A2A: MCP is for tools, A2A is for agents"
Concepts:
    - A2AServer(agent_factory=...) exposes a Strands agent with an Agent Card (/.well-known/agent-card.json).
    - A2AAgent(endpoint=...) consumes ANY remote A2A agent (Strands, LangGraph, ADK...) like a local agent,
      and can be used as a tool of another agent.
    - Requires: pip install 'strands-agents[a2a]'

Run (single file: starts the server in a background thread, then calls it):
    poetry run python local/ex_23_a2a.py
"""

import threading
import time

from strands import Agent, tool
from strands.agent.a2a_agent import A2AAgent
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer

model = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")


@tool
def get_fx_quote(currency: str, amount: float) -> dict:
    """Quote a currency conversion to COP for the treasury desk."""
    rates = {"USD": 3_950.0, "EUR": 4_280.0}
    rate = rates.get(currency.upper(), 0)
    return {"currency": currency, "amount": amount, "rate": rate, "cop": amount * rate}


def treasury_agent_factory(context_id: str) -> Agent:
    return Agent(
        name="AnyBank Treasury FX Agent",
        description="Quotes FX conversions to COP for AnyBank channels.",
        model=model,
        tools=[get_fx_quote],
        system_prompt="Eres la mesa de dinero (tesorería) de AnyBank. Responde en español con la cotización.",
        callback_handler=None,
    )


# ---- 1) Remote team: TREASURY exposes its agent via A2A ----
server = A2AServer(agent_factory=treasury_agent_factory, host="127.0.0.1", port=9001)
threading.Thread(target=server.serve, daemon=True).start()
time.sleep(3)

# ---- 2) Another team: the MOBILE APP agent consumes it via A2A ----
treasury_remote = A2AAgent(endpoint="http://127.0.0.1:9001")

# 2a) Direct call: a remote A2A agent behaves like a local agent
print("DIRECT A2A >", treasury_remote("Cotiza 100 EUR"))


# 2b) As a tool of another agent (wrap the remote call)
@tool
def treasury_fx(request: str) -> str:
    """Ask the AnyBank treasury desk (remote A2A agent) for an FX quote.

    Args:
        request: The quote request in natural language.
    """
    return str(treasury_remote(request))


app_agent = Agent(
    model=model,
    tools=[treasury_fx],
    system_prompt="Eres el asistente de la app de AnyBank. Usa treasury_fx para cotizaciones.",
    callback_handler=None,
)

print("APP AGENT>", app_agent("Cuántos pesos colombianos son 2.500 dólares hoy?"))
