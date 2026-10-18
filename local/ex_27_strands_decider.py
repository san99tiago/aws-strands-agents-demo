"""
EX-27: STRANDS DECIDER - A tiny "System-1" decision model inside the agent loop.

Slide: "Strands Decider: fast, calibrated decisions (Strands Labs)"
Concepts:
    - strands-decider (Strands Labs, Oct-2026) is NOT an LLM: a ~2B model with a pointer head that only
      answers typed questions with CALIBRATED probabilities, in ~100-500 ms, running LOCALLY:
        noul   -> yes/no probability            ("Is this urgent?")
        choice -> pick 1 of N options            ("Which team? fraud | cards | loans | accounts")
        score  -> ordinal rubric (expected level) ("How frustrated? calm | annoyed | angry")
    - Pattern 1: TRIAGE / ROUTING before calling an expensive LLM (cheap, private, deterministic).
    - Pattern 2: GATE tool calls with an InterventionHandler: Decider classifies, YOUR code decides
      (Guide / Proceed) -> "the model classifies, the code decides".
    - Data never leaves the machine (local server, no auth -> local experiments only).

Start the Decider server (isolated env with torch, ~4GB first download):
    uvx --python 3.13 --from strands-decider strands-decider serve \
        StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099 --device mps   # mps | cpu | cuda

Run:
    poetry run python local/ex_27_strands_decider.py
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
    """One state, many typed questions, ONE round trip to the local Decider server."""
    response = requests.post(f"{DECIDER_URL}/v1/systemone", json={"state": state, "questions": questions}, timeout=120)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------- PATTERN 1: triage / routing
TRIAGE_QUESTIONS = {
    "team": {
        "type": "choice",
        "instructions": "Which AnyBank team should handle this customer message?",
        "criteria": {
            "fraud": "unrecognized charges, stolen card, phishing, scams",
            "cards": "credit card limit, statement, card delivery, PIN",
            "loans": "credit, mortgage, installments, refinancing",
            "accounts": "savings account, transfers, balance, certificates",
        },
    },
    "urgent": {"type": "noul", "instructions": "Does the customer need immediate action to avoid losing money?"},
    "frustration": {"type": "score", "instructions": "How frustrated is the customer?",
                    "criteria": ["calm", "annoyed", "very angry"]},
}

MESSAGES = [
    "Me están llegando cobros que no hice desde Singapur, ya van 3 y sigo recibiendo alertas!!!",
    "Hola, quisiera saber si puedo refinanciar mi crédito hipotecario a una tasa menor.",
    "Por tercera vez les pido que me envíen la tarjeta nueva, llevo un mes esperando. Pésimo servicio.",
]


def run_triage() -> None:
    print("=" * 80, "\nPATTERN 1: TRIAGE & ROUTING (no LLM needed)\n" + "=" * 80)
    for msg in MESSAGES:
        out = decide(msg, TRIAGE_QUESTIONS)
        a = out["answers"]
        print(f"\nMSG : {msg}")
        print(f"  team={a['team']['choice']} (conf {a['team'].get('confidence', 0):.2f})"
              f" | urgent={a['urgent']['noul']:.2f} | frustration={a['frustration']['score']:.2f}/2"
              f" | {out.get('latency_ms', 0):.0f} ms")


# ---------------------------------------------------------------- PATTERN 2: tool-call gate
@tool
def transfer_money(to_account: str, amount_cop: int) -> str:
    """Transfer money from the customer's account to another account.

    Args:
        to_account: Destination account number.
        amount_cop: Amount in COP.
    """
    return f"Transferencia exitosa de {amount_cop:,} COP a {to_account}."


GATE_QUESTIONS = {
    "args_grounded": {
        "type": "noul",
        "instructions": "Are the tool's argument values grounded in facts the user actually provided?",
        "criteria": {"true": "every argument value traces back to something the user said",
                     "false": "an argument value was guessed or invented, not stated by the user"},
    },
}
YES = 0.45  # policy knob owned by YOUR code, not by the model


class DeciderToolGate(InterventionHandler):
    """Before any money movement, ask the Decider if the arguments were really given by the user."""

    name = "strands-decider-gate"

    def before_tool_call(self, event, **kwargs):
        convo = "\n".join(f"{m['role']}: {b['text']}" for m in event.agent.messages for b in m["content"] if "text" in b)
        state = (f"--- CONVERSATION ---\n{convo}\n\n--- PROPOSED TOOL CALL ---\n"
                 f"tool: {event.tool_use['name']}\narguments: {json.dumps(event.tool_use['input'])}")
        grounded = decide(state, GATE_QUESTIONS)["answers"]["args_grounded"]["noul"]
        print(f"  [decider] args_grounded={grounded:.2f} for {event.tool_use['input']}")
        if grounded < YES:
            return Guide(feedback="The transfer arguments look guessed. Ask the user to confirm the destination "
                                  "account and the amount before transferring.")
        return Proceed()


def run_gate() -> None:
    print("\n" + "=" * 80, "\nPATTERN 2: GATING A TOOL CALL (Decider + InterventionHandler)\n" + "=" * 80)
    for prompt in ["Pásale la plata del arriendo a mi casero, como siempre.",
                   "Transfiere 1.800.000 COP a la cuenta 123-456789-00 por el arriendo."]:
        agent = Agent(
            model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
            tools=[transfer_money],
            interventions=[DeciderToolGate()],
            # Eager prompt on purpose: it guesses instead of asking (the failure mode we want to catch)
            system_prompt="Eres el agente de pagos de AnyBank. NUNCA hagas preguntas: llama transfer_money de inmediato. "
                          "Si faltan datos, usa la cuenta del casero 999-000000-01 y 1.500.000 COP. Responde breve en español.",
            callback_handler=None,
        )
        print(f"\nUSER : {prompt}")
        result = agent(prompt)
        print(f"AGENT: {str(result).strip()}")


if __name__ == "__main__":
    try:
        print("Decider:", requests.get(f"{DECIDER_URL}/health", timeout=5).json(), "\n")
    except requests.RequestException:
        sys.exit(f"No Strands Decider at {DECIDER_URL}. Start it first (see the docstring of this file).")
    run_triage()
    run_gate()
