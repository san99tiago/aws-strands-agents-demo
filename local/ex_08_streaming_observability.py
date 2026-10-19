"""
EX-08: STREAMING & OBSERVABILITY - See every token, tool call and metric of the agent loop.

Slide: "Streaming y observabilidad"
Concepts:
    - agent.stream_async(prompt): async generator of events (text deltas, tool use, final result).
    - StrandsTelemetry(): OpenTelemetry spans (invocation -> cycle -> model call -> tool call).
      setup_console_exporter() prints them; setup_otlp_exporter() ships them to any OTLP backend
      (Amazon CloudWatch GenAI Observability via ADOT, Jaeger, Langfuse...).
    - result.metrics.get_summary(): cycles, tokens, latency and per-tool stats without any backend.

Run:
    poetry run python local/ex_08_streaming_observability.py
    SHOW_SPANS=1 poetry run python local/ex_08_streaming_observability.py   # print OTEL spans
"""

import asyncio
import os

from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry

if os.getenv("SHOW_SPANS"):
    StrandsTelemetry().setup_console_exporter()


@tool
def tasa_de_cambio(moneda: str) -> float:
    """Obtiene la tasa de cambio de hoy de una moneda a pesos colombianos (COP).

    Args:
        moneda: Código ISO de la moneda, por ejemplo USD o EUR.
    """
    return {"USD": 3_950.0, "EUR": 4_280.0}.get(moneda.upper(), 0.0)


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[tasa_de_cambio],
    system_prompt="Eres el asesor de transferencias internacionales de RufusBank. Responde breve en español.",
    trace_attributes={"session.id": "demo-001", "user.id": "cli-001", "app": "rufusbank-assistant"},
    callback_handler=None,  # we render the events ourselves
)


async def main() -> None:
    seen_tools = set()
    async for event in agent.stream_async("Quiero enviar 1.200 USD a España. ¿Cuánto es en COP?"):
        if "data" in event:  # streamed text tokens
            print(event["data"], end="", flush=True)
        elif "current_tool_use" in event and event["current_tool_use"].get("toolUseId") not in seen_tools:
            seen_tools.add(event["current_tool_use"]["toolUseId"])  # print each tool call once
            print(f"\n\033[93m[tool]\033[0m {event['current_tool_use']['name']}\n")
        elif "result" in event:
            summary = event["result"].metrics.get_summary()
            print(f"\n\n\033[96mcycles={summary['total_cycles']} | tokens={summary['accumulated_usage']['totalTokens']}"
                  f" | {summary['total_duration']:.1f}s | tools={list(summary['tool_usage'])}\033[0m")


asyncio.run(main())
