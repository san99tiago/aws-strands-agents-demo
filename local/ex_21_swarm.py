"""
EX-21: MULTI-AGENT (2/4) - Swarm: autonomous hand-offs between peers.

Slide: "Swarm: collaborative agents with shared context"
Concepts:
    - Swarm([agents], entry_point=...): agents get an automatic handoff_to_agent tool.
    - Shared working memory: each agent sees the task + history of previous agents.
    - Safety limits: max_handoffs, max_iterations, execution_timeout, repetitive hand-off detection.
    - Emergent path: the AGENTS decide who goes next (vs Graph where YOU define it).

Run:
    poetry run python local/ex_21_swarm.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import Swarm

model = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")


def make(name: str, prompt: str) -> Agent:
    return Agent(name=name, model=model, system_prompt=prompt, callback_handler=None)


intake = make("intake", "Recibes reclamos de clientes de AnyBank. Resume el caso en 2 líneas y entrega al especialista correcto.")
fraud = make("fraud_analyst", "Analista de fraude. Evalúa si es fraude (alto/medio/bajo) y entrega a customer_care con tu dictamen.")
disputes = make("disputes_analyst", "Analista de contracargos. Define si aplica disputa y el plazo. Entrega a customer_care.")
care = make("customer_care", "Redacta la respuesta final al cliente en español, empática, máx 5 líneas, con número de caso. NO entregues a nadie más.")

swarm = Swarm([intake, fraud, disputes, care], entry_point=intake, max_handoffs=6, execution_timeout=300)

result = swarm(
    "Me llegaron 3 cobros de 89.900 COP de 'GAMESHOP*INTL' anoche a las 3am y yo estaba dormido. "
    "Tengo la tarjeta conmigo."
)

print("Status :", result.status)
print("Path   :", " -> ".join(node.node_id for node in result.node_history))
print("\nFINAL  :", result.results[result.node_history[-1].node_id].result)
