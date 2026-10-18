"""
Local MCP SERVER (stdio) with generic AnyBank products - used by ex_06_mcp_local_custom.py

Built with FastMCP (official MCP Python SDK). Any MCP client (Strands, Kiro, Claude Code...)
can consume these tools.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("anybank-products")

PRODUCTS = {
    "cuenta-ahorros": {"name": "Cuenta de Ahorros Digital", "rate_ea": 9.5, "fee": 0},
    "cdt-90": {"name": "CDT 90 días", "rate_ea": 11.2, "fee": 0},
    "tc-clasica": {"name": "Tarjeta de Crédito Clásica", "rate_ea": 26.4, "fee": 18_900},
    "libre-inversion": {"name": "Crédito de Libre Inversión", "rate_ea": 19.8, "fee": 0},
}


@mcp.tool(description="List AnyBank financial products with their annual effective rate (EA %) and monthly fee (COP).")
def list_products() -> dict:
    return PRODUCTS


@mcp.tool(description="Simulate a fixed-rate loan. Returns the monthly installment in COP (French amortization).")
def simulate_loan(amount_cop: float, months: int, rate_ea: float = 19.8) -> dict:
    monthly_rate = (1 + rate_ea / 100) ** (1 / 12) - 1
    installment = amount_cop * monthly_rate / (1 - (1 + monthly_rate) ** -months)
    return {
        "amount_cop": amount_cop,
        "months": months,
        "rate_ea": rate_ea,
        "monthly_rate_pct": round(monthly_rate * 100, 4),
        "installment_cop": round(installment),
        "total_paid_cop": round(installment * months),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
