# 🩺 MedVoice AI: Streamlit Deployment Package

An autonomous Medical Voice AI Assistant web application built with **LangChain**, **OpenRouter**, **MedlinePlus (NIH XML Search API)**, and **Microsoft Edge Neural TTS**.

This directory is **self-contained and direct-ready-to-deploy** to **Streamlit Community Cloud**, **Docker**, **Render**, **Hugging Face Spaces**, or any cloud VM.

---

## Features

- **Autonomous Tool Calling**: Automatically calls the National Library of Medicine (MedlinePlus) API to retrieve verified clinical topics.
- **Curated Fallback Medical Knowledge**: Reliable responses even if external APIs or networks face interruptions.
- **Strict Medical Safety Guardrails**: Non-diagnostic, non-prescriptive, spoken-friendly responses designed with patient safety first.
- **Neural Speech Synthesis**: Powered by Microsoft Edge-TTS with multi-accent support (Indian, US, UK English voices).
- **Interactive Tool Inspection**: Expanders show exact queries and retrieved NIH XML summaries for complete transparency.
- **In-Browser Audio Player & MP3 Download**: Cross-platform audio playback compatible with all browsers and cloud containers.
- **Dynamic Key & Secret Management**: Works with Streamlit Secrets (`st.secrets`), `.env`, or manual browser entry.

---

## Directory Structure

```
lab4/streamlit_app/
├── .streamlit/
│   └── config.toml          # Custom theme & server configuration
├── app.py                   # Streamlit web application entry point
├── core_agent.py            # LangChain agent, MedlinePlus tool & Edge-TTS logic
├── requirements.txt         # Minimal, cloud-compatible dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules for secrets & cache
├── Dockerfile               # Container deployment configuration
└── README.md                # Deployment and local run documentation
```

---

## Quickstart: Running Locally

### 1. Navigate to this directory
```bash
cd lab4/streamlit_app
```

### 2. Create and activate a virtual environment
```bash
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in `lab4/streamlit_app/`:
```bash
cp .env.example .env
```
Add your OpenRouter key inside `.env`:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_MODEL=nvidia/nemotron-3.5-lightning:free
```

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## Deploying to Streamlit Community Cloud (Recommended)

Streamlit Community Cloud provides 100% free hosting directly linked to your GitHub repository.

### Step 1: Push to GitHub
Commit and push this repository to your GitHub account:
```bash
git add lab4/streamlit_app/
git commit -m "Add ready-to-deploy MedVoice AI Streamlit app"
git push origin main
```

### Step 2: Create a New App on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
2. Click **"New app"**.
3. Select your repository and branch (`main`).
4. Set **Main file path** to:
   ```
   lab4/streamlit_app/app.py
   ```
5. Click **"Advanced settings..."** (or open the App Settings after creation) -> **"Secrets"**.
6. Add your OpenRouter API key to the secrets block:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
   LLM_MODEL = "nvidia/nemotron-3.5-lightning:free"
   ```
7. Click **"Save"** and **"Deploy"**!

Your app will be live with a public URL in 1–2 minutes!

---

## Deploying with Docker

### Build the Image
```bash
docker build -t medvoice-ai:latest .
```

### Run the Container
```bash
docker run -p 8501:8501 -e OPENROUTER_API_KEY="your_api_key" medvoice-ai:latest
```
Access the application at `http://localhost:8501`.

---

## Supported Models

The app defaults to `nvidia/nemotron-3.5-lightning:free` on OpenRouter, which supports tool calling. Other tested models:
- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-2.0-flash-001`
- `openai/gpt-4o-mini`

---

## Medical & Educational Disclaimer

> [!WARNING]
> This application is created strictly for **educational and research demonstrations**. It does not provide medical diagnoses or prescriptions. Always consult a licensed healthcare provider for personal health concerns.
