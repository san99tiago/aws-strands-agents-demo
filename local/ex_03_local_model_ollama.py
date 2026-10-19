"""
EX-03: 100% LOCAL MODEL - Run the agent on YOUR PC, no cloud, no third party, no API key.

Slide: "Modelo local: todo en tu PC"
Model:
    Google Gemma 3 270M (gemma3:270m) -> the smallest Gemma: 270M params, ~290 MB, runs on CPU/Apple Silicon.

Setup (one time):
    1. Install Ollama (local inference engine): brew install ollama   (or https://ollama.com/download)
    2. Start the local server:                   ollama serve          (or: brew services start ollama)
    3. Download the model:                       ollama pull gemma3:270m
    4. Install the Strands extra:                pip install 'strands-agents[ollama]'

Concepts:
    - OllamaModel(host=..., model_id=...): same Agent API, the LLM now runs on localhost:11434.
    - Data never leaves your machine (privacy, offline demos, edge, labs).
    - Tiny models are fast and cheap but less capable: great for simple tasks, not for complex agents.

Run:
    poetry run python local/ex_03_local_model_ollama.py
"""

from strands import Agent
from strands.models.ollama import OllamaModel

local_model = OllamaModel(host="http://localhost:11434", model_id="gemma3:270m", temperature=0.2)

agent = Agent(model=local_model, system_prompt="Responde en español, en una sola frase.")
agent("¿Qué vino primero, el huevo o la gallina? - SOLO ELIGE UNO")
