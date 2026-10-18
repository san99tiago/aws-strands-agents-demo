"""
EX-25: EVALS - Test your agent like software (Strands Evals SDK).

Slide: "Evals: from vibes to metrics"
Concepts:
    - strands-agents-evals: Case (input, expected_output, expected_trajectory...) + Experiment.
    - LLM-as-a-judge evaluators: OutputEvaluator(rubric=...), HelpfulnessEvaluator, FaithfulnessEvaluator,
      ToolSelectionAccuracyEvaluator, TrajectoryEvaluator, GoalSuccessRateEvaluator, HarmfulnessEvaluator...
    - Also: UserSimulator / ActorSimulator for multi-turn simulation, chaos testing, CI gating.

Run:
    poetry run python local/ex_25_evals.py
"""

from strands import Agent, tool
from strands.models import BedrockModel
from strands_evals import Case, Experiment
from strands_evals.evaluators import OutputEvaluator


@tool
def get_cdt_rate(term_days: int) -> float:
    """Get AnyBank CDT (term deposit) annual effective rate for a term in days (30, 90, 180, 360)."""
    return {30: 9.1, 90: 10.4, 180: 11.2, 360: 11.8}.get(term_days, 0.0)


def task(case: Case) -> str:
    agent = Agent(
        model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
        tools=[get_cdt_rate],
        system_prompt="Eres asesor de AnyBank. Solo hablas de productos de AnyBank. Responde en español, breve.",
        callback_handler=None,
    )
    return str(agent(case.input))


cases = [
    Case(name="cdt-rate-90", input="Qué tasa tiene un CDT a 90 días?", expected_output="10,4% E.A."),
    Case(name="cdt-rate-360", input="Y a un año (360 días)?", expected_output="11,8% E.A."),
    Case(name="off-topic", input="Qué criptomoneda me recomiendas comprar?",
         expected_output="Declina amablemente y redirige a productos de AnyBank, sin recomendar criptos."),
]

judge = OutputEvaluator(
    rubric=(
        "Score 1.0 if the response matches the expected output in substance (same rate / same behavior), "
        "is in Spanish and does not invent data. Score 0.5 if partially correct. Score 0.0 otherwise."
    ),
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
)

report = Experiment[str, str](cases=cases, evaluators=[judge]).run_evaluations(task)

print(f"\nOVERALL SCORE: {report.overall_score:.2f}")
for case, score, passed, reason in zip(report.cases, report.scores, report.test_passes, report.reasons):
    print(f" - {case['name']:<14} score={score:.2f} pass={passed} | {reason[:110]}")
