import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CustomerOrderAgent")
BASE = "http://localhost:4000"

# Tools
@mcp.tool()
async def get_order(order_id: str) -> dict:
	"""Fetch order metadata by ID via the Node API."""
	async with httpx.AsyncClient(timeout=5) as client:
		r = await client.get(f"{BASE}/orders/{order_id}")
		r.raise_for_status()
		return r.json()

@mcp.tool()
async def track_order(order_id: str) -> dict:
    """Get tracking info for an order via Node API."""
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{BASE}/orders/{order_id}/tracking")
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def cancel_order(order_id: str) -> dict:
    """Cancel an order via Node API (policy enforced in Node)."""
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.post(f"{BASE}/orders/{order_id}/cancel")
        return {"status": r.status_code, "body": r.json()}

# Resources
@mcp.resource("policy://cancellation")
def cancellation_policy() -> str:
	"""Return the policy text used by the agent for decisions."""
	return "Orders placed < 10 days ago are eligible for cancellation."

if __name__ == "__main__":
	mcp.run()