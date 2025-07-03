# MCP SERVER FOR NAME GENERATION
# Used with STDIO for local examples

from mcp.server.fastmcp import FastMCP
import random

mcp = FastMCP("My name generator server.")


FIRST_NAMES = [
    "Santiago",
    "Monica",
    "Elkin",
    "Yesid",
    "Esteban",
    "David",
    "Daniel",
    "Melissa",
    "Camila",
    "Jorjhan",
    "Ruben",
    "Nazly",
]

LAST_NAMES = [
    "Garcia",
    "Hill",
    "Guerra",
    "Palencia",
    "Medina",
    "Upegui",
    "Vahos",
    "Mejia",
    "Yepes",
    "Leal",
    "Vargas",
    "Sadday",
    "Ramos",
]


@mcp.tool(
    name="generate_first_name",
    title="Generate First Name",
    description="Generate a First Name",
)
def generate_first_name() -> str:
    return random.choice(FIRST_NAMES)


@mcp.tool(
    name="generate_last_name",
    title="Generate Last Name",
    description="Generate a Last Name",
)
def generate_last_name() -> str:
    return random.choice(LAST_NAMES)


if __name__ == "__main__":
    mcp.run(transport="stdio")
