# Lab 3: Enterprise IT Helpdesk AI Assistant (LangChain & OpenRouter)

An enterprise-style AI Helpdesk Assistant built using **LangChain**, **OpenRouter**, and **Function Calling / Tool Execution**.

The AI Agent understands user requests, selects the appropriate tool to execute, inspects enterprise services/databases, and returns conversational, context-aware answers.

---

## Capabilities & Tools

The agent provides the following simulated enterprise tools:

| Tool | Description |
| :--- | :--- |
| `check_system_status` | Checks operational status of services (`wifi`, `vpn`, `email`, `github`). |
| `get_employee_information` | Retrieves employee directory details (department, office, device). |
| `create_ticket` | Creates an IT support ticket for an employee issue. |
| `search_it_policy` | Searches company IT policies (`password`, `vpn`, `software`, `wifi`). |
| `get_ticket_status` | Retrieves the status of existing IT support tickets. |

---

## Requirements

- Python 3.10+
- OpenRouter API Key ([openrouter.ai](https://openrouter.ai/))

---

## Setup Instructions

Activate the shared virtual environment created at the repository root (`agentic-ai-class/.venv`):

```bash
# From lab3 directory:
# Windows (CMD): ..\.venv\Scripts\activate
# Windows (PowerShell): ..\.venv\Scripts\Activate.ps1
# Linux/macOS: source ../.venv/bin/activate
```


### 3. Configure Environment Variables

Create or update `.env` in the `lab3` folder:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_MODEL=z-ai/glm-5.3-flash
```

---

## Running the Project

### Interactive CLI Mode

Run the complete assistant loop in the terminal:

```bash
python main.py
```

Or query with a single prompt:

```bash
python main.py "What is the status of ticket INC-1003?"
```

### Jupyter Notebook Mode

Run and explore the step-by-step code notebook:

```bash
jupyter notebook lab3.ipynb
# or open lab3.ipynb in VS Code / Antigravity IDE and select kernel (.venv)
```

---

## Architecture Flow

```
User Query
    │
    ▼
LLM (ChatOpenRouter / ChatOpenAI)
    │
    ▼
Reasoning & Decision Making
    │
    ▼
Tool Call (e.g. get_ticket_status, check_system_status)
    │
    ▼
Tool Execution (Python Function)
    │
    ▼
ToolMessage Result fed back to LLM
    │
    ▼
Final Assistant Response
```
