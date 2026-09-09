"""
Interactive CLI Assistant for Lab 5: Model Context Protocol (MCP) Assistant
Communicates with the College MCP Server to answer queries using dynamic tool calling.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
from client import is_server_reachable

load_dotenv()


async def run_cli():
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    model_name = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    api_key = os.getenv("OPENROUTER_API_KEY")

    print("=" * 65)
    print("  College MCP AI Assistant (Model Context Protocol & LangChain)")
    print("=" * 65)

    if not api_key:
        print("[Warning] OPENROUTER_API_KEY not found in .env file.")
        print("Please configure your OpenRouter API key in lab5/.env")
        print("=" * 65)
        sys.exit(1)

    # 1. Check MCP Server Availability
    reachable = await is_server_reachable(server_url)
    if not reachable:
        print(f"\n[Error] Unable to reach MCP Server at: {server_url}")
        print("\nPlease start the MCP server in a separate terminal:")
        print("    cd lab5")
        print("    python server.py\n")
        print("Then run this assistant again.")
        print("=" * 65)
        sys.exit(1)

    # 2. Connect via MCPAdapter and discover tools
    async with MCPAdapter(server_url) as adapter:
        tools = await adapter.list_tools()

        print(f"MCP Server Connected : {server_url}")
        print(f"Chat Model           : {model_name}")
        print(f"Discovered Tools ({len(tools)}):")
        for t in tools:
            desc = t.description.strip().splitlines()[0] if t.description else "No description"
            print(f"  • {t.name}: {desc}")
        print("=" * 65)

        # Initialize Chat Model & Agent
        model = get_chat_model(
            model_name=model_name,
            api_key=api_key,
            temperature=0
        )

        agent = create_agent(
            model=model,
            tools=tools
        )

        # Case A: Run with command line arguments (One-off mode)
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"\nUser: {query}")
            try:
                response = await agent.ainvoke({
                    "messages": [{"role": "user", "content": query}]
                })
                print(f"\nAssistant:\n{response['messages'][-1].content}\n")
            except Exception as e:
                print(f"\n[Error executing query]: {e}")
            return

        # Case B: Interactive REPL Mode
        print("\nInteractive Chat Mode:")
        print("Type your question below, or type 'exit' or 'quit' to end.")
        print("Special commands: 'tools' to re-list MCP tools, 'clear' to reset chat.\n")
        print("Sample Questions:")
        print(" • 'What are Praveen\'s AI marks?'")
        print(" • 'What is Ravi\'s attendance?'")
        print(" • 'Calculate the average marks of Ananya.'")
        print(" • 'Compare Ravi and Praveen\'s python marks.'\n")

        conversation_history = []

        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting. Goodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if user_input.lower() == "tools":
                print("\nAvailable MCP Server Tools:")
                for t in tools:
                    print(f"  • {t.name}: {t.description}")
                print()
                continue

            if user_input.lower() == "clear":
                conversation_history.clear()
                print("\n[Conversation history cleared.]\n")
                continue

            conversation_history.append({"role": "user", "content": user_input})

            print("\n[Agent reasoning with MCP tools...]")
            try:
                response = await agent.ainvoke({"messages": conversation_history})
                assistant_message = response["messages"][-1].content
                conversation_history.append({"role": "assistant", "content": assistant_message})
                print(f"\nAssistant:\n{assistant_message}\n")
            except Exception as e:
                print(f"\n[Error]: {e}\n")


def main():
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")


if __name__ == "__main__":
    main()
