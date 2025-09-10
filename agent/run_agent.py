from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStdio

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

client = OpenAI()
app = FastAPI()
session = SQLiteSession("orders_chat")

mcp_server: MCPServerStdio | None = None
agent: Agent | None = None

class MessageIn(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    global mcp_server, agent
    mcp_server = MCPServerStdio(
        params={
            "command": "uv",
            "args": ["run", "python", "../mcp-customer-orders/server.py"],
        },
        cache_tools_list=True,
    )
    await mcp_server.connect()
    agent = Agent(
        name="Orders Assistant",
        model="gpt-4.1",
        instructions = """
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
            """,
        mcp_servers=[mcp_server]
    )

@app.on_event("shutdown")
async def shutdown_event():
    if mcp_server:
        await mcp_server.close()

@app.post("/chat")
async def chat(inp: MessageIn):
    result = await Runner.run(agent, inp.message, session=session)
    return {"response": result.final_output}

app.mount("/", StaticFiles(directory="static", html=True), name="static")