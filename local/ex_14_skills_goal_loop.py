"""
EX-14: AGENT SKILLS + GOAL LOOP - Load know-how on demand, iterate until the goal is met.

Slide: "Skills y GoalLoop"
Concepts:
    - AgentSkills plugin: each skill is a folder with SKILL.md (AgentSkills.io standard, same as Kiro/Claude Code).
      Only NAME + DESCRIPTION go into the prompt; the full instructions are LOADED INTO CONTEXT on demand
      (progressive disclosure -> fewer tokens, more expertise).
    - GoalLoop plugin: after each answer a JUDGE model checks the goal; if it fails, the feedback is
      loaded back into the context and the agent retries automatically (max_attempts).

Run:
    poetry run python local/ex_14_skills_goal_loop.py
"""

import os

from strands import Agent, AgentSkills
from strands.models import BedrockModel
from strands.vended_plugins.goal import GoalLoop, JudgeConfig

haiku = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")
sonnet = BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1")

# ---------------------------------------------------------------- 1. AGENT SKILLS
skills_agent = Agent(
    model=sonnet,
    plugins=[AgentSkills(skills=os.path.join(os.path.dirname(__file__), "skills"))],  # kyc-onboarding, fraud-triage
    system_prompt="Eres el asistente omnicanal de RufusBank. Responde en español.",
)
skills_agent("Quiero abrir una cuenta. Soy Mateo Ríos, CC 1020304050, soy independiente y gano 24 millones al mes.")
print("\n\nTools used (skills loaded on demand):", list(skills_agent.event_loop_metrics.tool_metrics))

# ---------------------------------------------------------------- 2. GOAL LOOP
print("\n" + "=" * 70)
goal_agent = Agent(
    model=haiku,
    plugins=[GoalLoop(
        goal=("Descripción de una cuenta de ahorros que: (1) tiene máximo 4 frases, (2) menciona la tasa como "
              "'efectiva anual (E.A.)', (3) incluye 'Producto vigilado por la Superintendencia Financiera de Colombia', "
              "(4) nunca promete ganancias garantizadas."),
        judge=JudgeConfig(model=sonnet),
        max_attempts=3,
    )],
    system_prompt="Eres copywriter de marketing de RufusBank. Muy vendedor.",
    callback_handler=None,
)
result = goal_agent("Escribe la descripción de la Cuenta Ahorro Rufus al 9,5% para la app. ¡Que la gente se haga rica!")
print(str(result).strip(), "\n\nmodel calls:", result.metrics.cycle_count)
