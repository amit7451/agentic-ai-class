"""
Model Context Protocol (MCP) Client
Connects to the College MCP Server, inspects tools, and runs agent workflows.
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Try importing ChatOpenRouter, fallback to ChatOpenAI with openrouter base_url
try:
    from langchain_openrouter import ChatOpenRouter
    def get_chat_model(model_name: str, api_key: str, temperature: float = 0):
        return ChatOpenRouter(
            model=model_name,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=temperature
        )
except ImportError:
    from langchain_openai import ChatOpenAI
    def get_chat_model(model_name: str, api_key: str, temperature: float = 0):
        return ChatOpenAI(
            model=model_name,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=temperature
        )

from langchain.mcp import MCPAdapter
from langchain.agents import create_agent

load_dotenv()

DEFAULT_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")


async def is_server_reachable(url: str = DEFAULT_SERVER_URL) -> bool:
    """Checks if the MCP server is listening and reachable."""
    # Strip endpoint to check base or post empty ping
    base_url = url.split("/mcp")[0]
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(base_url)
            return resp.status_code in [200, 404, 405]
    except Exception:
        return False


async def discover_tools(server_url: str = DEFAULT_SERVER_URL):
    """Connects to the MCP server and returns the list of registered tools."""
    async with MCPAdapter(server_url) as adapter:
        return await adapter.list_tools()


async def query_mcp_agent(query: str, server_url: str = DEFAULT_SERVER_URL, model_name: str = DEFAULT_MODEL) -> str:
    """Creates a LangChain agent bound to the MCP server tools and returns the answer."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment or .env file.")

    async with MCPAdapter(server_url) as adapter:
        tools = await adapter.list_tools()

        model = get_chat_model(
            model_name=model_name,
            api_key=api_key,
            temperature=0
        )

        agent = create_agent(
            model=model,
            tools=tools
        )

        response = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": query}
            ]
        })

        return response["messages"][-1].content


async def main():
    print(f"Connecting to MCP Server at: {DEFAULT_SERVER_URL}")
    reachable = await is_server_reachable(DEFAULT_SERVER_URL)
    if not reachable:
        print(f"[Error] Could not connect to MCP server at {DEFAULT_SERVER_URL}.")
        print("Please start the server first in another terminal:")
        print("    python server.py")
        sys.exit(1)

    print("Server reachable! Discovering tools...")
    tools = await discover_tools(DEFAULT_SERVER_URL)
    print(f"Discovered {len(tools)} tools:")
    for tool in tools:
        print(f" - {tool.name}: {tool.description}")

    query = "What are Praveen's AI marks and what is his attendance?"
    print(f"\nRunning test query: '{query}'")
    try:
        answer = await query_mcp_agent(query)
        print(f"\nAssistant Response:\n{answer}")
    except Exception as e:
        print(f"\nAgent execution encountered an error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
