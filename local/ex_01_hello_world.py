"""
EX-01: HELLO WORLD - Your first agent with Strands Agents.

Slide: "Hello World"
Setup:
    pip install strands-agents        # or: poetry add strands-agents
    AWS credentials active (default model runs on Amazon Bedrock)

Concepts:
    - from strands import Agent      -> the whole SDK starts here.
    - Agent(...)                     -> model + system prompt + (optional) tools = an agent.
    - Calling the agent runs the full AGENT LOOP and returns the answer.

Run:
    poetry run python local/ex_01_hello_world.py
"""

from strands import Agent

result = Agent(system_prompt="Eres un experto en liderazgo. Responde en español.")("Dime 3 frases famosas de Jeff Bezos")
