# AI Chatbot For Customer Orders

## Overview

This project implements an AI-powered chatbot that can give information about, and cancel, customer orders (subject to policy). The chatbot controls an MCP (Model Control Protocol) server and interacts with REST API endpoints exposed by a node server.

Using the MCP server, the chatbot can call tools that allow it to:
* pull order information
* check the cancellation policy
* cancel an order
* cancel one item in an order.

The project also defines some structured tests that can be run to test the chatbot's decision-making.

## Architecture
```
User ---> Simple Browser UI ---> AI Chatbot ---> MCP Server ---> API
```
* **Simple Browser UI**:  The user can type their message, hit send, and see the response and chat history.
* **Chatbot (AI Layer)**: Parses user input and generates commands/responses.
* **MCP Server**: Manages execution and enforces structured request handling.
* **API**: Exposes endpoints for reading from and writing to the orders database.


## Project Structure

* `agent`
    * Runs the UI and AI chatbot (`run_agent.py`)
    * Defines structured tests (`run_tests.py`)
* `mcp-customer-orders`
    * Contains the MCP server code (tool definitions)
* `orders-api`
    * Contains the database of customer orders (`lib/db.ts`)
    * Exposes API endpoints that can be used to run operations on the database (`routes/orders.ts`)
* `experiment.md`
    * Contains high-level descriptions of experiments that have been run on the chatbot.

## Setup

```bash
# Clone repository
git clone https://github.com/taiddon-pixel/orders-agent.git
cd orders-agent

# Install dependencies

# API
cd orders-api
npm install

# AI agent
cd ../agent
uv venv
source .venv/bin/activate
uv sync

# Store OpenAI API key in environment
echo "OPENAI_API_KEY=<your-api-key>" > .env
```

## Usage

### Run the server
```bash
cd ../orders-api
pnpm dev
```
### Run the agent (in another window)

```bash
cd ../agent
source .venv/bin/activate # if not already activated
uv run uvicorn run_agent:app --reload --port 8000
```

Open the resulting link in your browser and interact with the chatbot however you'd like!

## Testing

Assuming you have already run the **Setup** instructions, and the API is running, you can run a test as follows:

```bash
cd agent # if not already in this folder
source .venv/bin/activate # if not already activated
python run_tests.py --test <your-test>
```

`<your-test>` can be any of:

```
"cancel_order"
"cancel_item"
"cancel_ineligible"
"list_orders"
"vague_order_request"
```

Outputs will appear in `agent/logs/`. You can compare them with the contents of `agent/example_logs/`.

If you want to reset the database between tests (recommended), kill the API and re-run `pnpm dev` in that terminal. (Future work would make this behaviour more graceful i.e. automatically resetting the database at the end of a test run.)