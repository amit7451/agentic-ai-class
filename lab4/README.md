# Lab 4: Autonomous Medical Voice AI Assistant (LangChain, MedlinePlus & Voice AI)

An educational Medical Information Voice Assistant built using **LangChain**, **OpenRouter**, **MedlinePlus (NIH XML API)**, **Faster-Whisper (STT)**, and **Edge-TTS (TTS)**.

The AI Agent listens to patient inquiries, searches the National Library of Medicine (MedlinePlus) via function/tool calling, applies medical safety guardrails, and synthesizes clear, concise spoken audio answers.

---

## Architecture & Workflow

```
[Patient Speech / Text Input]
            │
            ▼
[Speech Recognition (Faster-Whisper)] (Optional Voice Mode)
            │
            ▼
[LangChain Agent (OpenRouter LLM)]
            │
            ├─► Tool Calling Decision
            │        │
            │        ▼
            │   [medical_information Tool] ──► [MedlinePlus NIH API]
            │        │                              │
            │        └─────── Return XML Results ◄──┘
            │
            ▼
[Educational Safety Guardrails]
- No medical diagnosis
- No medicine prescriptions
- Spoken-friendly (concise, plain language, no markdown)
            │
            ▼
[Text-to-Speech (Microsoft Edge Neural TTS)]
            │
            ▼
[Spoken Audio Response (`medical_response.mp3`)]
```

---

## Capabilities & Tools

| Tool / Component | Description |
| :--- | :--- |
| `medical_information` | Queries MedlinePlus (`https://wsearch.nlm.nih.gov/ws/query`) for peer-reviewed health topics and educational summaries. |
| **System Safety Guardrails** | Enforces strict non-diagnostic, non-prescriptive medical assistance with spoken-friendly phrasing. |
| **Edge-TTS** | Async Neural Text-to-Speech generation using `en-IN-NeerjaNeural` (or custom voices). |
| **Faster-Whisper** | Fast, local CPU-optimized Speech-to-Text for converting microphone recordings to prompt text. |

---

## Requirements

- Python 3.10+
- OpenRouter API Key ([openrouter.ai](https://openrouter.ai/))
- Microphone and speakers (optional, for voice mode)

---

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Navigate to the lab4 directory:
cd lab4

# Create virtual environment:
py -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (Command Prompt):
.venv\Scripts\activate.bat

# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create or update `.env` in the `lab4` directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_MODEL=nvidia/nemotron-3.5-lightning:free
```

---

## Running the Application

### Option A: Interactive CLI Assistant (`main.py`)

Run the assistant in interactive text mode:
```bash
python main.py
```

Run with voice synthesis enabled (speaks answers aloud):
```bash
python main.py --voice
```

Run a one-off query directly:
```bash
python main.py "Can you tell me about hypertension?"
python main.py --voice "What is asthma and how is it managed?"
```

### Option B: Jupyter Notebook (`lab4.ipynb`)

1. Start Jupyter Notebook or open in VS Code / Antigravity IDE:
   ```bash
   code lab4.ipynb
   ```
2. Select the kernel: **Python (Lab 4 .venv)**.
3. Run through each section sequentially:
   - Cell 1: Environment & API Key Verification
   - Cell 2: Chat Model Initialization
   - Cell 3: General Medical Knowledge Check
   - Cell 4: MedlinePlus Tool Definition
   - Cell 5: Tool Binding & Test Invocation
   - Cell 6: Speech Recognition (Whisper Model Setup)
   - Cell 7: Speech Synthesis (Edge-TTS Setup)
   - Cell 8: End-to-End Voice Medical Assistant Execution

---

## Important Medical Disclaimer

> [!WARNING]
> This project is for **educational and research purposes only**. It does **not** provide medical advice, diagnosis, or treatment recommendations. Always consult a qualified healthcare provider with any medical questions.
