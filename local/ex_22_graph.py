"""
EX-22: MULTI-AGENT (3/4) - Graph: deterministic workflows with conditional edges.

Slide: "Graph: you define the flow, agents do the work"
Concepts:
    - GraphBuilder: add_node(agent, id) + add_edge(a, b, condition=fn) + set_entry_point(id).
    - Nodes run when ALL their dependencies finished (parallel branches supported).
    - Conditional edges = business routing (e.g. only escalate if risk is HIGH).
    - Nodes can be Agents OR other multi-agent systems (Swarm inside a Graph).

Flow:
    extractor --> risk_scorer --(HIGH)--> human_review_memo
                              \\-(LOW/MEDIUM)--> auto_approval_letter

Run:
    poetry run python local/ex_22_graph.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder

model = BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1")


def make(name: str, prompt: str) -> Agent:
    return Agent(name=name, model=model, system_prompt=prompt, callback_handler=None)


extractor = make("extractor", "Extrae en JSON: nombre, ingreso_mensual, monto, plazo_meses, deudas_actuales.")
risk_scorer = make(
    "risk_scorer",
    "Calcula riesgo de crédito. Regla: si cuota_estimada/ingreso > 0.35 o hay mora previa => RIESGO: HIGH. "
    "Si no => RIESGO: LOW. Responde la línea 'RIESGO: <HIGH|LOW>' y una justificación de 1 línea.",
)
human_review = make("human_review_memo", "Escribe un memo de 3 viñetas para el comité de crédito explicando por qué requiere revisión.")
auto_letter = make("auto_approval_letter", "Escribe una carta corta (máx 6 líneas) de pre-aprobación al cliente en español, firmada por AnyBank.")


def is_high_risk(state) -> bool:
    return "RIESGO: HIGH" in str(state.results["risk_scorer"].result).upper()


def is_low_risk(state) -> bool:
    return not is_high_risk(state)


builder = GraphBuilder()
builder.add_node(extractor, "extractor")
builder.add_node(risk_scorer, "risk_scorer")
builder.add_node(human_review, "human_review_memo")
builder.add_node(auto_letter, "auto_approval_letter")
builder.add_edge("extractor", "risk_scorer")
builder.add_edge("risk_scorer", "human_review_memo", condition=is_high_risk)
builder.add_edge("risk_scorer", "auto_approval_letter", condition=is_low_risk)
builder.set_entry_point("extractor")
graph = builder.build()

for application in [
    "Soy Pedro, gano 3.000.000 al mes, pido 40.000.000 a 24 meses y estuve en mora el año pasado.",
    "Soy Ana, gano 12.000.000 al mes, pido 10.000.000 a 36 meses, sin deudas.",
]:
    result = graph(application)
    path = " -> ".join(node.node_id for node in result.execution_order)
    last = result.execution_order[-1].node_id
    print(f"\nINPUT : {application}\nPATH  : {path}\nOUTPUT: {str(result.results[last].result).strip()[:400]}")
