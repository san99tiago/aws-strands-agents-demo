from strands import Agent
from strands_tools import calculator, current_time

# Create agent with default tools
agent = Agent(tools=[calculator, current_time])

# Give possible messages that will intentionally use tools
message = """
Cuánto falta para Diciembre 31 del 2025???
"""

# Agent will use the shell and file reader tool when appropriate
agent(message)
