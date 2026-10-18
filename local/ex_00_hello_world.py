"""
EX-00: HELLO WORLD - The smallest possible Strands Agent.

Slide: "Your first agent in 3 lines"
Concepts:
    - Agent() with ZERO config uses Amazon Bedrock + the SDK default model
      (global.anthropic.claude-sonnet-4-6 as of strands-agents 1.61).
    - Calling the agent runs the full AGENT LOOP and returns an AgentResult.

Run:
    poetry run python local/ex_00_hello_world.py
"""

from strands import Agent

agent = Agent()
result = agent("En una frase: qué es un agente de IA para un banco?")

print("\n\n--- AgentResult ---")
print("stop_reason :", result.stop_reason)  # end_turn | tool_use | interrupt | ...
print("tokens      :", result.metrics.accumulated_usage)
