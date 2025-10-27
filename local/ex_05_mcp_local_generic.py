from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands_tools import current_time
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel

# Connect to an MCP server using stdio transport
stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.nova-canvas-mcp-server@latest"],
            env={"AWS_REGION": "us-east-1"},
        )
    )
)

bedrock_model1 = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    params={"max_tokens": 1600, "temperature": 0.7},
)

# Create an agent with MCP tools
with stdio_mcp_client:
    # Get the tools from the MCP server
    tools = stdio_mcp_client.list_tools_sync()
    tools.append(current_time)

    # Create an agent with these tools
    agent = Agent(model=bedrock_model1, tools=tools)
    agent(
        "Quiero que me generes una imagen de medellin en Palmas con una vista a la ciudad."
    )
