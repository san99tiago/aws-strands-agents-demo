"""
EX-18: GOAL LOOP - Iterate until a judge says the output meets the goal.

Slide: "GoalLoop: self-refinement against a validator"
Concepts:
    - GoalLoop(goal=..., max_attempts=N) plugin: after each answer a JUDGE model validates it;
      if it fails, feedback is fed back and the agent retries automatically.
    - goal can be a natural-language rubric OR a Python Validator function (deterministic checks).
    - Great for regulated content: disclosures, formats, reading level, length limits.

Run:
    poetry run python local/ex_18_goal_loop.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.vended_plugins.goal import GoalLoop, JudgeConfig

compliance_goal = GoalLoop(
    goal=(
        "A product description of a savings account for a Colombian bank that: "
        "(1) is at most 4 sentences, "
        "(2) mentions the rate as 'tasa efectiva anual (E.A.)', "
        "(3) includes the phrase 'Producto vigilado por la Superintendencia Financiera de Colombia', "
        "(4) never promises guaranteed profits."
    ),
    judge=JudgeConfig(model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")),
    max_attempts=3,
)

agent = Agent(
    model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", region_name="us-east-1"),
    plugins=[compliance_goal],
    system_prompt="Eres copywriter de marketing de AnyBank. Escribe en español, muy vendedor.",
    callback_handler=None,
)

result = agent("Escribe la descripción de la Cuenta Ahorro Plus al 9,5% para la app. Que la gente se haga rica!")
print(str(result).strip())
print("\nstop_reason:", result.stop_reason, "| model calls:", result.metrics.cycle_count)
