from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands_tools import current_time
from strands.tools.mcp import MCPClient

# Connect to an MCP server using stdio transport
stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-api-mcp-server@latest"],
            env={"AWS_REGION": "us-east-1"},
        )
    )
)

# Create an agent with MCP tools
with stdio_mcp_client:
    # Get the tools from the MCP server
    tools = stdio_mcp_client.list_tools_sync()
    tools.append(current_time)

    # Create an agent with these tools
    agent = Agent(tools=tools)
    agent("Cuáles fueron mis gastos de AWS el mes pasado?")
