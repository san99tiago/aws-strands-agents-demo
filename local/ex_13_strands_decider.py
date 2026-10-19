"""
EX-13: STRANDS DECIDER - A tiny "System-1" decision model inside the agent loop.

Slide: "Strands Decider"
Concepts:
    - An LLM GENERATES tokens (free text). The Decider CHOOSES: it only answers typed questions with
      calibrated probabilities, in ~100-500 ms, running LOCALLY (~2B params, Strands Labs):
        noul   -> yes/no probability      ("Is it urgent?")
        choice -> pick 1 of N options     ("Which team? fraud | cards | loans | accounts")
        score  -> ordinal level           ("How frustrated? calm | annoyed | angry")
    - Pattern 1: TRIAGE / ROUTING before calling an expensive LLM.
    - Pattern 2: GATE a tool call with an InterventionHandler -> "the model classifies, YOUR code decides".

Start the Decider server (isolated env with torch, ~4GB first download):
    uvx --python 3.13 --from strands-decider strands-decider serve \
        StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099 --device mps   # mps | cpu | cuda

Run:
    poetry run python local/ex_13_strands_decider.py
"""

import json
import os
import sys

import requests
from strands import Agent, tool
from strands.interventions import Guide, InterventionHandler, Proceed
from strands.models import BedrockModel

DECIDER_URL = os.getenv("STRANDS_DECIDER_URL", "http://127.0.0.1:8099")


def decide(state: str, questions: dict) -> dict:
    """One state, many typed questions, ONE round trip to the local Decider."""
    response = requests.post(f"{DECIDER_URL}/v1/systemone", json={"state": state, "questions": questions}, timeout=120)
    response.raise_for_status()
    return response.json()["answers"]


# ------------------------------------------------------------ PATTERN 1: triage / routing (no LLM)
TRIAGE = {
    "equipo": {
        "type": "choice",
        "instructions": "Which RufusBank team should handle this customer message?",
        "criteria": {
            "fraudes": "unrecognized charges, stolen card, phishing, scams",
            "tarjetas": "credit card limit, statement, card delivery, PIN",
            "creditos": "loans, mortgage, installments, refinancing",
            "cuentas": "savings account, transfers, balance, certificates",
        },
    },
    "urgente": {"type": "noul", "instructions": "Does the customer need immediate action to avoid losing money?"},
    "frustracion": {"type": "score", "instructions": "How frustrated is the customer?",
                    "criteria": ["calm", "annoyed", "very angry"]},
}

MENSAJES = [
    "Me están llegando cobros que no hice desde Singapur, ya van 3 y sigo recibiendo alertas!!!",
    "Hola, quisiera saber si puedo refinanciar mi crédito hipotecario a una tasa menor.",
    "Por tercera vez les pido la tarjeta nueva, llevo un mes esperando. Pésimo servicio.",
]


# ------------------------------------------------------------ PATTERN 2: gate a money movement
@tool
def transferir(cuenta_destino: str, monto_cop: int) -> str:
    """Transfiere dinero desde la cuenta del cliente a otra cuenta.

    Args:
        cuenta_destino: Número de la cuenta destino.
        monto_cop: Monto en COP.
    """
    return f"Transferencia exitosa de {monto_cop:,} COP a {cuenta_destino}."


GATE = {"args_grounded": {
    "type": "noul",
    "instructions": "Are the tool's argument values grounded in facts the user actually provided?",
    "criteria": {"true": "every argument value traces back to something the user said",
                 "false": "an argument value was guessed or invented, not stated by the user"},
}}


class DeciderGate(InterventionHandler):
    """Before moving money, ask the Decider if the arguments really came from the user."""

    name = "rufusbank-decider-gate"
    UMBRAL = 0.45  # policy knob owned by YOUR code, not by the model

    def before_tool_call(self, event, **kwargs):
        chat = "\n".join(f"{m['role']}: {b['text']}" for m in event.agent.messages for b in m["content"] if "text" in b)
        state = f"{chat}\n\nPROPOSED TOOL CALL: {event.tool_use['name']} {json.dumps(event.tool_use['input'])}"
        p = decide(state, GATE)["args_grounded"]["noul"]
        print(f"  [decider] args_grounded={p:.2f} -> {'Proceed' if p >= self.UMBRAL else 'Guide'}")
        if p < self.UMBRAL:
            return Guide(feedback="Los datos de la transferencia parecen inventados. Pide al usuario la cuenta y el monto.")
        return Proceed()


if __name__ == "__main__":
    try:
        requests.get(f"{DECIDER_URL}/health", timeout=5)
    except requests.RequestException:
        sys.exit(f"No Strands Decider at {DECIDER_URL}. Start it first (see the docstring).")

    print("=" * 70, "\nPATTERN 1: TRIAGE (Decider only, no LLM)\n" + "=" * 70)
    for msg in MENSAJES:
        a = decide(msg, TRIAGE)
        print(f"\n{msg}\n  -> equipo={a['equipo']['choice']} ({a['equipo'].get('confidence', 0):.2f})"
              f" | urgente={a['urgente']['noul']:.2f} | frustración={a['frustracion']['score']:.2f}/2")

    print("\n" + "=" * 70, "\nPATTERN 2: GATE A TOOL CALL (Decider + InterventionHandler)\n" + "=" * 70)
    for prompt in ["Pásale la plata del arriendo a mi casero, como siempre.",
                   "Transfiere 1.800.000 COP a la cuenta 123-456789-00 por el arriendo."]:
        agent = Agent(
            model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
            tools=[transferir],
            interventions=[DeciderGate()],
            # The model "knows" a frequent payment from its prompt, but the USER never stated it in this chat:
            # exactly the kind of non-grounded argument the Decider gate should catch.
            system_prompt="Eres el agente de pagos de RufusBank. Llama la tool transferir de inmediato, sin preguntar. "
                          "Pago frecuente del cliente: arriendo -> cuenta 999-000000-01 por 1.500.000 COP. "
                          "Si el usuario da otra cuenta o monto, usa SIEMPRE los datos del usuario. Responde breve en español.",
            callback_handler=None,
        )
        print(f"\nUSER : {prompt}\nAGENT: {str(agent(prompt)).strip()}")
