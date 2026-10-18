"""
EX-03: MULTIPLE TOOLS + JUST-IN-TIME CONTEXT - The model picks and chains tools.

Slide: "Tool selection & chaining"
Concepts:
    - Several built-in tools at once: the model chooses which one(s) to call, in order.
    - python_repl runs code through the agent SANDBOX (default = local host, NOT isolated!).
      For production use a real Sandbox (DockerSandbox, SshSandbox or AgentCore Code Interpreter).
    - ContextInjector plugin: injects fresh context (today's date) before each model call
      WITHOUT polluting the conversation history (replaces the deprecated current_time tool).

Run:
    poetry run python local/ex_03_multiple_default_tools.py
"""

from datetime import date

from strands import Agent
from strands.models import BedrockModel
from strands.vended_plugins.context_injector import ContextInjector
from strands.vended_tools import http_request, python_repl

today_injector = ContextInjector(lambda context: f"<context>Fecha de hoy: {date.today().isoformat()}</context>")

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[http_request, python_repl],
    plugins=[today_injector],
    system_prompt=(
        "Eres un asesor de ahorro de AnyBank. Para cualquier cálculo financiero usa SIEMPRE python_repl. "
        "Responde en español y de forma breve."
    ),
)

agent(
    "Si ahorro 350 USD cada mes desde hoy hasta el 31 de diciembre de 2027, con un interés del 0,8% mensual "
    "compuesto, cuánto tendré al final? Dámelo en USD y en COP usando la tasa de "
    "https://open.er-api.com/v6/latest/USD"
)

print("\n\nTools used:", list(agent.event_loop_metrics.tool_metrics.keys()))
print("Messages in history:", len(agent.messages), "(the injected date is NOT stored)")
