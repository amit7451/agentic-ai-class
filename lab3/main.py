import os
import sys
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

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


# ==========================================
# 1. Define Enterprise IT Tools
# ==========================================

@tool
def check_system_status(system: str) -> str:
    """
    Check the operational status of an enterprise system (e.g. wifi, vpn, email, github).
    """
    systems = {
        "wifi": "Wi-Fi service is operational.",
        "vpn": "VPN service is operational.",
        "email": "Email service is operational.",
        "github": "GitHub service is operational."
    }

    return systems.get(
        system.lower(),
        f"No status information is available for {system}."
    )


@tool
def get_employee_information(employee_name: str) -> str:
    """
    Retrieve employee information from the enterprise directory.
    """
    employees = {
        "rahul": {
            "department": "Finance",
            "office": "Hyderabad",
            "device": "Dell Latitude 5440"
        },
        "priya": {
            "department": "Engineering",
            "office": "Bangalore",
            "device": "Lenovo ThinkPad"
        },
        "arjun": {
            "department": "HR",
            "office": "Delhi",
            "device": "HP EliteBook"
        }
    }

    employee = employees.get(employee_name.lower())

    if not employee:
        return f"No employee information found for {employee_name}."

    return (
        f"Employee: {employee_name}\n"
        f"Department: {employee['department']}\n"
        f"Office: {employee['office']}\n"
        f"Device: {employee['device']}"
    )


@tool
def create_ticket(employee_name: str, issue: str) -> str:
    """
    Create an IT support ticket for an employee.
    """
    ticket_id = "INC-1001"

    return (
        f"Ticket created successfully.\n"
        f"Ticket ID: {ticket_id}\n"
        f"Employee: {employee_name}\n"
        f"Issue: {issue}\n"
        f"Status: Open"
    )


@tool
def search_it_policy(query: str) -> str:
    """
    Search the company's IT policies (e.g. password, vpn, software, wifi).
    """
    policies = {
        "password": (
            "Employees must change their password every 90 days. "
            "Passwords must contain uppercase, lowercase, numbers, "
            "and special characters."
        ),
        "vpn": (
            "Employees must use the approved company VPN when accessing "
            "internal systems from outside the corporate network."
        ),
        "software": (
            "Employees must request approval from IT before installing "
            "company-managed software."
        ),
        "wifi": (
            "Employees should connect company devices to the approved "
            "corporate Wi-Fi network."
        )
    }

    query_lower = query.lower()

    for keyword, policy in policies.items():
        if keyword in query_lower:
            return policy

    return "No matching IT policy was found."


@tool
def get_ticket_status(ticket_id: str) -> str:
    """
    Retrieve the current status of an IT support ticket.
    """
    tickets = {
        "INC-1001": "Open - IT technician has been assigned.",
        "INC-1002": "Resolved - Password was successfully reset.",
        "INC-1003": "In Progress - VPN issue is being investigated."
    }

    return tickets.get(
        ticket_id.upper(),
        f"Ticket {ticket_id} was not found."
    )


TOOLS = [
    check_system_status,
    get_employee_information,
    create_ticket,
    get_ticket_status,
    search_it_policy
]

TOOLS_BY_NAME = {t.name: t for t in TOOLS}


# ==========================================
# 2. Agent Execution Workflow
# ==========================================

def run_agent_turn(model_with_tools, messages: list):
    """
    Runs a turn with the model, executes any tool calls, and returns the final response.
    """
    response = model_with_tools.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        print(f"\n[Tool Execution Required: {len(response.tool_calls)} call(s)]")
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            print(f" -> Calling Tool: '{tool_name}' with args: {tool_args} (ID: {tool_id})")

            tool_fn = TOOLS_BY_NAME.get(tool_name)
            if tool_fn:
                tool_output = tool_fn.invoke(tool_args)
            else:
                tool_output = f"Error: Tool '{tool_name}' not recognized."

            print(f" -> Result: {tool_output}")

            tool_message = ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_id
            )
            messages.append(tool_message)

        # Get the final model response after feeding tool results back
        final_response = model_with_tools.invoke(messages)
        messages.append(final_response)
        return final_response
    else:
        return response


def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")

    model_name = "openrouter/free"
    print("=" * 60)
    print(" Enterprise IT Helpdesk AI Assistant (LangChain Agent)")
    print("=" * 60)
    print(f"Loaded OpenRouter API Key.")
    print(f"Using Model: {model_name}")
    print("Available Tools:")
    for t in TOOLS:
        print(f" - {t.name}: {t.description.strip().splitlines()[0]}")
    print("=" * 60)

    model = get_chat_model(model_name, api_key)
    model_with_tools = model.bind_tools(TOOLS)

    # If run with command line argument, execute once
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\nUser: {query}")
        messages = [HumanMessage(content=query)]
        response = run_agent_turn(model_with_tools, messages)
        print(f"\nAssistant:\n{response.content}\n")
        return

    # Interactive Loop
    print("\nAsk a question or type 'exit' to quit.\nExamples:")
    print(" - 'What is the status of ticket INC-1003?'")
    print(" - 'Who is Rahul and what device does he use?'")
    print(" - 'Check if our VPN is working.'")
    print(" - 'What is the company policy for passwords?'\n")

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        conversation_history.append(HumanMessage(content=user_input))
        response = run_agent_turn(model_with_tools, conversation_history)
        print(f"\nAssistant:\n{response.content}\n")


if __name__ == "__main__":
    main()
