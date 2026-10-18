"""
EX-11: INSIDE THE AGENT LOOP - Watch every cycle, event and token in real time.

Slide: "The Agent Loop (Model -> Tool -> Model -> ... -> Answer)"
Concepts:
    - stream_async(): async generator of events (text deltas, tool use, tool results, final result).
    - Each CYCLE = 1 model call (+ the tool calls it requested). Loop stops on stop_reason == end_turn.
    - The harness (SDK) owns: tool execution, message history, retries, metrics.
      The MODEL owns: reasoning, planning, which tool, when to stop -> "model-driven orchestration".

Run:
    poetry run python local/ex_11_agent_loop_streaming.py
"""

import asyncio

from strands import Agent, tool
from strands.models import BedrockModel


@tool
def get_fx_rate(currency: str) -> float:
    """Get today's exchange rate from the given currency to COP.

    Args:
        currency: ISO currency code, e.g. USD or EUR.
    """
    return {"USD": 3_950.0, "EUR": 4_280.0}.get(currency.upper(), 0.0)


@tool
def get_transfer_fee(amount_cop: float) -> float:
    """Get the international transfer fee (COP) for an amount in COP.

    Args:
        amount_cop: Amount to transfer in COP.
    """
    return round(max(25_000, amount_cop * 0.005))


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-haiku-5-5", region_name="us-east-1"),
    tools=[get_fx_rate, get_transfer_fee],
    system_prompt="Eres un asesor de transferencias internacionales de AnyBank. Responde breve en español.",
    callback_handler=None,  # we render the events ourselves
)


async def main() -> None:
    prompt = "Quiero enviar 1.200 USD a España. Cuánto es en COP y cuánto pago de comisión?"
    print(f"USER > {prompt}\n")
    cycle = 0
    async for event in agent.stream_async(prompt):
        if event.get("start_event_loop"):
            cycle += 1
            print(f"\n\033[95m--- CYCLE {cycle}: model call ---\033[0m")
        if "data" in event:  # streamed text tokens
            print(event["data"], end="", flush=True)
        if "message" in event and event["message"]["role"] == "assistant":
            for block in event["message"]["content"]:
                if "toolUse" in block:
                    print(f"\n\033[93m[toolUse]\033[0m {block['toolUse']['name']}({block['toolUse']['input']})")
        if "message" in event and event["message"]["role"] == "user":
            for block in event["message"]["content"]:
                if "toolResult" in block:
                    print(f"\033[92m[toolResult]\033[0m {block['toolResult']['content']}")
        if "result" in event:
            result = event["result"]
            print(f"\n\n\033[96m=== DONE: stop_reason={result.stop_reason} | cycles={cycle} "
                  f"| tokens={result.metrics.accumulated_usage['totalTokens']}\033[0m")


asyncio.run(main())
