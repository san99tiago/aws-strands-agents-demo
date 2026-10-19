"""
EX-06: MCP (Model Context Protocol) - Plug a remote MCP server as tools.

Slide: "MCP en Strands"
MCP server:
    AWS Knowledge MCP Server (remote, managed by AWS, no auth needed)
    https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server
    Endpoint: https://knowledge-mcp.global.api.aws

Concepts:
    - MCPClient(url=...) -> Streamable HTTP transport.
    - MCPClient is a ToolProvider: pass it DIRECTLY in Agent(tools=[...]); the SDK opens/closes the session.
    - Up-to-date AWS docs, what's new, blogs and regional availability -> no stale model knowledge.

Run:
    poetry run python local/ex_06_mcp_aws_knowledge.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

aws_knowledge = MCPClient(url="https://knowledge-mcp.global.api.aws")

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[aws_knowledge],
    system_prompt="Eres arquitecto de soluciones AWS. Usa SIEMPRE la documentación oficial y cita las URLs. Responde en español.",
)

agent(
    "Dame información actualizada de Amazon Bedrock AgentCore Runtime: qué es y cuáles son sus timeouts "
    "(sesión, inactividad, payload). Responde en máximo 6 viñetas."
)
