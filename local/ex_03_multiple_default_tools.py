from strands import Agent
from strands_tools import calculator, current_time
from strands.models import BedrockModel

bedrock_model = BedrockModel(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# Create agent with default tools
agent = Agent(model=bedrock_model, tools=[calculator, current_time])

# Give possible messages that will intentionally use tools
message = """
Cuánto falta para el Diciembre 31 del 2025???
"""

# Agent will use the shell and file reader tool when appropriate
agent(message)
