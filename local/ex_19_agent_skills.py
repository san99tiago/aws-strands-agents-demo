"""
EX-19: AGENT SKILLS - Package know-how as SKILL.md folders (AgentSkills.io standard).

Slide: "Skills: progressive disclosure of expertise"
Concepts:
    - A Skill = folder with SKILL.md (YAML front-matter name/description + instructions + resources).
    - AgentSkills plugin: only NAME + DESCRIPTION go into the system prompt (cheap).
      The full instructions are loaded ON DEMAND via a tool when the model decides it needs them.
    - Same SKILL.md format used by Kiro, Claude Code and other agents -> portable know-how.

Run:
    poetry run python local/ex_19_agent_skills.py
"""

import os

from strands import Agent, AgentSkills
from strands.models import BedrockModel

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")

agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    plugins=[AgentSkills(skills=SKILLS_DIR)],
    system_prompt="Eres el asistente omnicanal de AnyBank. Responde en español.",
)

agent(
    "Hola, quiero abrir una cuenta. Soy Mateo Ríos, CC 1020304050, nací el 3/5/1990, soy independiente "
    "(desarrollador freelance) y gano 24 millones al mes, la mitad en dólares (unos 3.000 USD)."
)
print("\n\nTools used:", list(agent.event_loop_metrics.tool_metrics.keys()))
