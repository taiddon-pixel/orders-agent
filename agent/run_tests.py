from dotenv import load_dotenv
import argparse
import os
import anyio
import httpx
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Tuple, Dict, Any
import sys
from contextlib import contextmanager

from agents import Agent, Runner, SQLiteSession, ToolCallItem
from agents.mcp import MCPServerStdio
from openai import OpenAI

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

client = OpenAI()

os.makedirs('logs', exist_ok=True)

default_instructions = """
You are an assistant that helps with tracking and canceling orders.
Always:
- Check the order status before canceling.
- Enforce the cancellation policy (orders < 10 days old).
- Cite the policy when refusing cancellations.
- Double check the customer definitely wants to cancel an order before proceeding.
You can assume all orders in the database are associated with the current user, 
so it is safe to find orders based on vague or incomplete input.
Ensure you only promise capabilities that are *available in the MCP tool definitions*
(e.g. you can't set up email reminders, weekly updates, returns).
Make answers friendly but concise."
"""

async def run_test(
    *,
    instructions: str = default_instructions,
    mcp_command: str = "uv",
    mcp_args: list[str] = ["run", "python", "../mcp-customer-orders/server.py"],
    user_prompts: list[str],
) -> None:
    """
    Creates MCP stdio server and Agent, cleans up automatically.
    """
    server = MCPServerStdio(
        params={"command": mcp_command, "args": mcp_args},
        cache_tools_list=True,
    )
    await server.connect()
    agent = Agent(
        name="Orders Assistant",
        model="gpt-4.1",
        instructions=instructions,
        mcp_servers=[server],
    )
    responses = []
    tool_calls = {}
    session = SQLiteSession("cancel_order.sqlite")
    for u in user_prompts:
        result = await Runner.run(starting_agent=agent, input=u, session=session)
        responses.append(result.final_output)
        for item in result.new_items:
            if isinstance(item, ToolCallItem):
                raw_item = json.loads(item.raw_item.model_dump_json())
                name = raw_item["name"]
                args = raw_item["arguments"]
                status = raw_item["status"]
                tool_calls[name] = {"args": args, "status": status}
    return { "responses": responses, "tool_calls": tool_calls }

async def test_cancel_order():
    result = await run_test(user_prompts=["Cancel my order A123.", "Yes I'm sure, please cancel the order."])
    calls = result['tool_calls']
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://localhost:4000/orders/A123')
    db_entry = resp.json()
    outstr = ''
    outstr+=f"Ran get_order? - {'get_order' in calls.keys()}\n"
    if 'get_order' in calls.keys():
        outstr+=f"Used correct id for get_order? - {calls['get_order']['args'] == '{"order_id":"A123"}'}\n"
    else:
        outstr+=f"Used correct id for get_order? - N/A\n"
    outstr+=f"Checked cancellation policy? - {'get_cancellation_policy' in calls.keys()}\n"
    outstr+=f"Called cancel_entire_order? - {'cancel_entire_order' in calls.keys()}\n"
    if 'cancel_entire_order' in calls.keys():
        outstr+=f"Cancelled the order using the correct id? - {calls['cancel_entire_order']['args'] == '{"order_id":"A123"}'}\n"
        outstr+=f"Cancelled the order successfully? - {db_entry['status'] == 'cancelled'}\n"
    else:
        outstr+=f"Cancelled the order using the correct id? - N/A\n"
        outstr+=f"Cancelled the order successfully? - N/A\n"
    with open(f'logs/test_cancel_order.log', 'w') as l:
        l.write(outstr)

async def test_cancel_order_item():
    result = await run_test(user_prompts=["Cancel my order item SKU1.", "Yes I'm sure, please cancel the order."])
    calls = result['tool_calls']
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://localhost:4000/orders/A123')
    db_entry = resp.json()
    outstr = ''
    outstr+=f"Checked cancellation policy? - {'get_cancellation_policy' in calls.keys()}\n"
    outstr+=f"Ran cancel one item? - {'cancel_one_item' in calls.keys()}\n"
    if 'cancel_one_item' in calls.keys():
        outstr+=f"Cancelled the item using the correct id? - {calls['cancel_one_item']['args'] == '{"order_id":"A123","sku":"SKU1"}'}\n"
        outstr+=f"Cancelled the order successfully? - {db_entry['items'][0]['status'] == 'cancelled'}\n"
    else:
        outstr+=f"Cancelled the item using the correct id? - N/A\n"
        outstr+=f"Cancelled the order successfully? - N/A\n"
    with open(f'logs/test_cancel_order_item.log', 'w') as l:
        l.write(outstr)

async def test_cancel_ineligible_order():
    result = await run_test(user_prompts=["Cancel my order B456"])
    calls = result['tool_calls']
    async with httpx.AsyncClient() as client:
        resp = await client.get('http://localhost:4000/orders/B456')
    db_entry = resp.json()
    outstr = ''
    outstr+=f"Checked cancellation policy? - {'get_cancellation_policy' in calls.keys()}\n"
    outstr+=f"Refused to cancel? - {'cancel_one_item' not in calls.keys() and 'cancel_entire_order' not in calls.keys()}\n"
    with open(f'logs/test_cancel_ineligible_order.log', 'w') as l:
        l.write(outstr)

async def test_list_orders():
    result = await run_test(user_prompts=["What are my orders?"])
    calls = result['tool_calls']
    with open(f'logs/test_list_orders.log', 'w') as l:
        l.write(f"Called get_all_orders? - {'get_all_orders' in calls.keys()}")

async def test_vague_order_request():
    result = await run_test(user_prompts=["I ordered some coffee thing, can you pull the order please."])
    calls = result['tool_calls']
    full_response = " ".join(result["responses"])
    outstr = ''
    outstr+=f"Ran get_all_orders? - {'get_all_orders' in calls.keys()}\n"
    outstr+=f"Called out the correct ID? - {'A123' in full_response}"
    with open(f'logs/test_vague_order_request.log', 'w') as l:
        l.write(outstr)

if __name__ == "__main__":
    TESTS = {
        "cancel_order": test_cancel_order,
        "cancel_item": test_cancel_order_item,
        "cancel_ineligible": test_cancel_ineligible_order,
        "list_orders": test_list_orders,
        "vague_order_request": test_vague_order_request
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, required=True, help="Which test to run")
    args = parser.parse_args()
    available_tests = list(TESTS.keys())
    if args.test not in available_tests:
        sys.exit(f"Please pass --test with one of the following arguments: {available_tests}")
    anyio.run(TESTS[args.test])
