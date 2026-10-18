"""
EX-15: INTERVENTIONS (the "Decider" layer) - Typed decisions over every agent action.

Slide: "Interventions: Proceed | Deny | Guide | Confirm | Transform"
Concepts:
    - InterventionHandler = a policy/decision point plugged into the agent loop.
      Override only the lifecycle methods you need: before_invocation, before_model_call,
      after_model_call, before_tool_call, after_tool_call.
    - Each method returns a typed decision:
        Proceed()            -> continue
        Deny(reason=...)     -> block (the model sees the reason and adapts)
        Guide(feedback=...)  -> steer the model with feedback (it retries / re-plans)
        Confirm(prompt=...)  -> ask a human (see ex_16)
        Transform(apply=fn)  -> mutate the event in place (e.g. sanitize inputs)
    - Several handlers compose in order (Deny short-circuits). on_error='deny' -> fail-closed.
    - Vended handlers: HumanInTheLoop, CedarAuthorization (pip install 'strands-agents[cedar]').

Run:
    poetry run python local/ex_15_interventions_decider.py
"""

from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent
from strands.interventions import Deny, Guide, InterventionHandler, Proceed, Transform
from strands.models import BedrockModel

SANCTIONED_ACCOUNTS = {"CO-999-000"}


@tool
def transfer_money(from_account: str, to_account: str, amount_cop: int, concept: str) -> str:
    """Transfer money between accounts.

    Args:
        from_account: Source account.
        to_account: Destination account.
        amount_cop: Amount in COP.
        concept: Short description of the transfer.
    """
    return f"OK: {amount_cop:,} COP de {from_account} a {to_account} ({concept})."


class AmlSanctionsDecider(InterventionHandler):
    """Hard rule: never transfer to sanctioned accounts (fail-closed)."""

    name = "aml-sanctions"
    on_error = "deny"

    def before_tool_call(self, event: BeforeToolCallEvent, **kwargs):
        if event.tool_use["name"] == "transfer_money" and event.tool_use["input"]["to_account"] in SANCTIONED_ACCOUNTS:
            return Deny(reason="Cuenta destino en lista restrictiva (SARLAFT). Transferencia bloqueada.")
        return Proceed()


class TransferLimitDecider(InterventionHandler):
    """Soft rule: above the daily limit -> guide the model to split / ask for confirmation."""

    name = "daily-limit"
    DAILY_LIMIT = 10_000_000

    def before_tool_call(self, event: BeforeToolCallEvent, **kwargs):
        if event.tool_use["name"] == "transfer_money" and event.tool_use["input"]["amount_cop"] > self.DAILY_LIMIT:
            return Guide(feedback=f"El monto supera el tope diario de {self.DAILY_LIMIT:,} COP. "
                                  "No ejecutes la transferencia; explica el límite y ofrece alternativas.")
        return Proceed()


class ConceptSanitizer(InterventionHandler):
    """Transform: normalize the transfer concept (trim + uppercase) before execution."""

    name = "concept-sanitizer"

    def before_tool_call(self, event: BeforeToolCallEvent, **kwargs):
        if event.tool_use["name"] != "transfer_money":
            return Proceed()

        def _apply(e: BeforeToolCallEvent) -> None:
            e.tool_use["input"]["concept"] = e.tool_use["input"]["concept"].strip().upper()

        return Transform(apply=_apply)


def new_agent() -> Agent:
    return Agent(
        model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
        tools=[transfer_money],
        interventions=[AmlSanctionsDecider(), TransferLimitDecider(), ConceptSanitizer()],
        system_prompt="Eres el agente de pagos de AnyBank. La cuenta del cliente es CO-111-222. Responde breve en español.",
        callback_handler=None,
    )


for prompt in [
    "Transfiere 250.000 a la cuenta CO-333-444 por el arriendo de octubre del apartamento",
    "Transfiere 15.000.000 a la cuenta CO-333-444 por la compra de la moto",
    "Transfiere 500.000 a la cuenta CO-999-000 por servicios",
]:
    print(f"\nUSER > {prompt}\nAGENT> {str(new_agent()(prompt)).strip()}")
