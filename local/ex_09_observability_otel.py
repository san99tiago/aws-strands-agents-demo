"""
EX-09: OBSERVABILITY - OpenTelemetry traces + metrics out of the box.

Slide: "You can't improve what you can't see"
Concepts:
    - StrandsTelemetry(): OTEL traces for invocation -> cycle -> model call -> tool call spans.
    - setup_console_exporter() prints spans; setup_otlp_exporter() sends them to any OTLP backend
      (Jaeger, Langfuse, Datadog, Amazon CloudWatch GenAI Observability via ADOT...).
    - trace_attributes: tag spans with session / user / business metadata.
    - result.metrics.get_summary(): tokens, latency, cycles and per-tool stats WITHOUT any backend.

Optional local backend (Jaeger UI at http://localhost:16686):
    docker run -d -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

Run:
    poetry run python local/ex_09_observability_otel.py
"""

import json
import os
import random

from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

telemetry = StrandsTelemetry()
if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    telemetry.setup_otlp_exporter()  # send traces to OTLP endpoint (Jaeger, ADOT, Langfuse...)
    telemetry.setup_meter(enable_otlp_exporter=True)
elif os.getenv("SHOW_SPANS"):
    telemetry.setup_console_exporter()  # print raw spans to console


@tool
def get_balance(customer_id: str) -> str:
    """Get the account balance (COP) of a customer.

    Args:
        customer_id: Customer identifier.
    """
    return f"Saldo de {customer_id}: {random.randint(100_000, 9_000_000):,} COP"


@tool
def block_card(customer_id: str, reason: str) -> str:
    """Block the debit card of a customer (e.g. lost or stolen).

    Args:
        customer_id: Customer identifier.
        reason: Why the card is being blocked.
    """
    return f"Tarjeta de {customer_id} bloqueada. Motivo: {reason}. Radicado #{random.randint(10000, 99999)}"


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_balance, block_card],
    system_prompt="Eres el asistente de AnyBank. Responde en español.",
    trace_attributes={"session.id": "demo-session-001", "user.id": "cust-001", "app": "anybank-assistant"},
)

result = agent("Perdí mi tarjeta, bloquéala por favor y dime cuánto saldo tengo. Soy cust-001.")

summary = result.metrics.get_summary()
print("\n\n=== METRICS SUMMARY ===")
print("cycles        :", summary["total_cycles"])
print("total duration:", round(summary["total_duration"], 2), "s")
print("usage         :", summary["accumulated_usage"])
print("tools         :", json.dumps({k: v["execution_stats"] for k, v in summary["tool_usage"].items()}, indent=2))
