import os
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# Connect to an MCP server using stdio transport
stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python", args=[os.path.join(os.path.dirname(__file__), "main.py")]
        )
    )
)
# Create an agent with MCP tools
with stdio_mcp_client:
    # Get the tools from the MCP server
    tools = stdio_mcp_client.list_tools_sync()

    # Create an agent with these tools
    agent = Agent(
        tools=tools,
        system_prompt="You are a specialized agent called BRUJO that helps in generation of different things",
    )

    # Loop for user's input until "exit"
    while True:
        user_input = input("\n\nUser: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye my friend!")
            break
        if not user_input:
            continue
        print("Agent: ", end="")
        agent(user_input)
