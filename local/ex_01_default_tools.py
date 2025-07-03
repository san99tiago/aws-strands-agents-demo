from strands import Agent
from strands_tools import calculator, current_time

# Create agent with default tools
agent = Agent(tools=[calculator, current_time])

# Give possible messages that will intentionally use tools
message = """
I am born in September 3rd 1999. How old am I in days and years?
"""

# Agent will use the shell and file reader tool when appropriate
agent(message)
