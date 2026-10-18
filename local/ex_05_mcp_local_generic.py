"""
EX-05: MCP (Model Context Protocol) - Plug ANY existing MCP server as tools.

Slide: "MCP: the USB-C of agent tools"
Concepts:
    - MCPClient is a ToolProvider: pass it DIRECTLY to Agent(tools=[...]).
      The SDK manages start/stop of the MCP session (no 'with' block needed).
    - MCPClient.load_servers(): reuse the same "mcpServers" JSON you use in Kiro / Claude Code.
    - prefix: namespace tools to avoid collisions; tool_filters: allow/deny specific tools.

Requires: uvx (https://docs.astral.sh/uv/)

Run:
    poetry run python local/ex_05_mcp_local_generic.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

MCP_CONFIG = {
    "mcpServers": {
        "aws-docs": {
            "command": "uvx",
            "args": ["awslabs.aws-documentation-mcp-server@latest"],
            "env": {"FASTMCP_LOG_LEVEL": "ERROR"},
        }
    }
}

mcp_clients = MCPClient.load_servers(MCP_CONFIG, prefix_with_server_name=True)

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=mcp_clients,  # <- managed lifecycle
    system_prompt="Eres un arquitecto de soluciones AWS para banca. Usa la documentación oficial y cita la URL.",
)

agent(
    "Según la documentación oficial de AWS, qué es Amazon Bedrock AgentCore Runtime "
    "y cuánto tiempo máximo puede durar una sesión? Responde en 4 viñetas en español."
)
print("\n\nMCP tools used:", list(agent.event_loop_metrics.tool_metrics.keys()))
