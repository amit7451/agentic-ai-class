# Lab 5: Model Context Protocol (MCP) AI Assistant (LangChain & MCP Server)

An educational implementation of the **Model Context Protocol (MCP)** using **FastMCP / MCPServer**, **LangChain MCP Adapters**, **OpenRouter**, and **Agentic Tool Calling**.

In this lab, the agent dynamically connects to an external MCP Server over **Streamable HTTP**, inspects available tools and schemas at runtime, and autonomously invokes remote tools to answer queries regarding student marks, attendance, and academic performance.

---

## Architecture & Workflow

```
┌─────────────────────────────────────────────────────────┐
│                      Client Side                        │
│                                                         │
│  [User Query / Terminal REPL / Jupyter Notebook]        │
│                         │                               │
│                         ▼                               │
│  [LangChain Agent (OpenRouter LLM)]                     │
│                         │                               │
│                         ▼                               │
│  [langchain.mcp.MCPAdapter (Client)]                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          │ HTTP (Streamable HTTP)
                          │ POST /mcp (JSON-RPC)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server Side                       │
│                                                         │
│  [College MCP Server (http://127.0.0.1:8000/mcp)]       │
│                         │                               │
│        ┌────────────────┴────────────────┐              │
│        ▼                ▼                ▼              │
│  [get_student]     [get_marks]    [get_attendance]      │
│        │                │                │              │
│        └────────────────┼────────────────┘              │
│                         ▼                               │
│             [calculate_average Tool]                    │
│                         │                               │
│                         ▼                               │
│             [In-Memory College DB]                      │
└─────────────────────────────────────────────────────────┘
```

---

## Capabilities & Remote MCP Tools

The **College MCP Server** registers and exposes the following tools:

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `get_student` | `name: str` | Retrieves complete student profile, all subject marks, and attendance percentage. |
| `get_marks` | `name: str` | Retrieves individual subject marks (`python`, `ai`, `dbms`). |
| `get_attendance` | `name: str` | Retrieves student attendance percentage and status. |
| `calculate_average` | `name: str` | Computes the mathematical average of marks across all enrolled subjects. |

---

## Requirements

- Python 3.10+
- OpenRouter API Key ([openrouter.ai](https://openrouter.ai/))
- MCP Server running locally or remotely

---

## Setup Instructions

Activate the shared virtual environment created at the repository root (`agentic-ai-class/.venv`):

```bash
# From lab5 directory:
# Windows (CMD): ..\.venv\Scripts\activate
# Windows (PowerShell): ..\.venv\Scripts\Activate.ps1
# Linux/macOS: source ../.venv/bin/activate
```

### Configure Environment Variables

Create or update `.env` in the `lab5` directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_MODEL=nvidia/nemotron-3-super-120b-a12b:free
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
MCP_SERVER_URL=http://localhost:8000/mcp
```

---

## Running the Project

### Step 1: Start the MCP Server

In a dedicated terminal, launch the College MCP server:

```bash
python server.py
```

Expected output:
```text
============================================================
 College MCP Server (Model Context Protocol)
============================================================
Server Name: College Server
Transport  : streamable-http
Endpoint   : http://127.0.0.1:8000/mcp
Registered Tools:
 - get_student(name: str)
 - get_marks(name: str)
 - get_attendance(name: str)
 - calculate_average(name: str)
============================================================
Starting server... (Press Ctrl+C to stop)
```

### Step 2: Run the Assistant

Open a second terminal with the virtual environment activated.

#### Option A: Interactive CLI Mode (`main.py`)

Run the complete conversational loop:

```bash
python main.py
```

Sample session:
```text
You: What are Praveen's AI marks?
Assistant: Praveen scored 88 in AI.

You: What is Ravi's attendance and calculate his average marks?
Assistant: Ravi's attendance is 87%, and his average marks across subjects is 84.33.

You: Who has higher marks in Python between Ravi and Praveen?
Assistant: Praveen scored 92 in Python while Ravi scored 85, so Praveen scored higher.
```

#### Option B: Single-Query CLI Execution

Run a one-off query directly from the command line:

```bash
python main.py "What are Praveen's AI marks?"
python main.py "Calculate the average marks of Ravi."
```

#### Option C: Client Verification Script (`client.py`)

Verify tool discovery and direct MCP adapter invocation:

```bash
python client.py
```

#### Option D: Jupyter Notebook Mode (`lab5.ipynb`)

Launch the notebook to inspect step-by-step code and execution:

```bash
jupyter notebook lab5.ipynb
# or open lab5.ipynb in VS Code / Antigravity IDE and select the (.venv) kernel
```

---

## Why Model Context Protocol (MCP)?

1. **Decoupled Architecture**: Tools and data resources run as independent services. The AI client does not need to host or bundle the execution code directly.
2. **Dynamic Runtime Discovery**: The client dynamically discovers tool signatures and argument schemas over standard JSON-RPC.
3. **Enterprise Scalability**: Multiple agents can safely interact with centralized servers and governed databases via standard access policies.
