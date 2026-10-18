"""
EX-02: ONE BUILT-IN TOOL - The agent decides WHEN to use a tool.

Slide: "Tools = the hands of the agent"
Concepts:
    - Built-in ("vended") tools ship inside the SDK: strands.vended_tools
      (http_request, shell, file_editor, python_repl, notebook, sleep, subagent...).
    - The model reads the tool spec (name + description + schema) and emits a toolUse.
    - The SDK executes it and feeds the toolResult back into the loop.

Run:
    poetry run python local/ex_02_single_default_tool.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.vended_tools import http_request

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[http_request],
    system_prompt="Eres un analista financiero de AnyBank. Usa APIs públicas cuando necesites datos en vivo.",
)

agent(
    "Consulta https://open.er-api.com/v6/latest/USD y dime a cuánto está el dólar "
    "en pesos colombianos (COP) y en euros (EUR) hoy."
)

print("\n\nTools used:", list(agent.event_loop_metrics.tool_metrics.keys()))
