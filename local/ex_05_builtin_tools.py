"""
EX-05: BUILT-IN (PRE-INSTALLED) TOOLS - Ready-to-use tools, zero code.

Slide: "Built-in tools (Pre-Instaladas)"
Concepts:
    - strands.vended_tools ships tools: http_request, python_repl, shell, file_editor,
      notebook, handoff_to_user, subagent, mcp_router, sleep...
    - The model picks and CHAINS tools: http_request (live FX rate) -> python_repl (exact math).
    - python_repl runs on the agent sandbox (local host by default, NOT isolated!).
      In production use an isolated sandbox (Docker or AgentCore Code Interpreter).

Run:
    poetry run python local/ex_05_builtin_tools.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.vended_tools import http_request, python_repl

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[http_request, python_repl],
    system_prompt="Eres asesor de ahorro de RufusBank. Para cálculos usa SIEMPRE python_repl. Responde breve en español.",
)

agent(
    "Si ahorro 350 USD al mes durante 24 meses al 0,8% mensual compuesto, ¿cuánto tendré? "
    "Dámelo en USD y en COP con la tasa de https://open.er-api.com/v6/latest/USD"
)
