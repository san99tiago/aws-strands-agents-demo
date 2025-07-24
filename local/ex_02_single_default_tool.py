from strands import Agent
from strands_tools import http_request

agent = Agent(tools=[http_request])
print(agent("Cuál es el clima en Medellín?"))
