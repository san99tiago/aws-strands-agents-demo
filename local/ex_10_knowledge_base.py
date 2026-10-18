"""
EX-10: RAG WITH BEDROCK KNOWLEDGE BASES - Ground answers in your documents.

Slide: "RAG as a tool (agentic retrieval)"
Concepts:
    - Agentic RAG: the agent DECIDES when to search, can re-query and combine sources.
    - Tool calls bedrock-agent-runtime.retrieve() and returns chunks + sources.
    - (Alternative) strands_tools.retrieve or the MemoryManager + BedrockKnowledgeBaseStore.

Set your KB:
    export KB_ID=XXXXXXXXXX

Run:
    poetry run python local/ex_10_knowledge_base.py
"""

import os

import boto3
from strands import Agent, tool
from strands.models import BedrockModel

KB_ID = os.getenv("KB_ID", "NKWD6MZBBG")  # "knowledge-base-bancos-general-001"
kb_client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


@tool
def search_bank_docs(query: str, max_results: int = 5) -> list[dict]:
    """Search the bank's official documentation (products, fees, FAQs, policies).

    Args:
        query: Natural-language search query, in Spanish.
        max_results: Number of chunks to retrieve.
    """
    response = kb_client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": max_results}},
    )
    return [
        {
            "text": r["content"]["text"][:1200],
            "score": round(r.get("score", 0), 3),
            "source": r.get("location", {}).get("s3Location", {}).get("uri")
            or r.get("location", {}).get("webLocation", {}).get("url"),
        }
        for r in response["retrievalResults"]
    ]


agent = Agent(
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-5-5", region_name="us-east-1"),
    tools=[search_bank_docs],
    system_prompt=(
        "Eres RUFFY, asistente bancario. Responde SOLO con base en search_bank_docs. "
        "Si no encuentras la respuesta, dilo. Cita la fuente al final."
    ),
)

if __name__ == "__main__":
    print("\nRUFFY + Knowledge Base (escribe 'exit' para salir)")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if q.lower() in {"exit", "quit"}:
            break
        if q:
            agent(q)
