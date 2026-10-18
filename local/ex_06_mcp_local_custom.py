"""
EX-06: CUSTOM MCP SERVER - Expose your own business capabilities via MCP.

Slide: "Build once, reuse everywhere (MCP)"
Concepts:
    - mcp_server_anybank.py = a FastMCP stdio server (products + loan simulator).
    - MCPClient(lambda: stdio_client(...)) = explicit transport factory.
    - Interactive chat loop: the agent keeps conversation memory between turns.

Run:
    poetry run python local/ex_06_mcp_local_custom.py
    (type 'exit' to quit)
"""

import os
import sys

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

SERVER = os.path.join(os.path.dirname(__file__), "mcp_server_anybank.py")

anybank_mcp = MCPClient(
    lambda: stdio_client(StdioServerParameters(command=sys.executable, args=[SERVER])),
    prefix="anybank",
)

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[anybank_mcp],
    system_prompt=(
        "Eres ANDY, asesor comercial de AnyBank. Usa las herramientas MCP para productos y simulaciones. "
        "Responde en español con cifras en COP."
    ),
)

print("ANDY (AnyBank) - escribe 'exit' para salir. Ej: 'Simula un crédito de 20 millones a 36 meses'")
while True:
    try:
        user_input = input("\n\nUser: ").strip()
    except EOFError:
        break
    if user_input.lower() in {"exit", "quit"}:
        print("Chao parce!")
        break
    if user_input:
        print("ANDY: ", end="")
        agent(user_input)
