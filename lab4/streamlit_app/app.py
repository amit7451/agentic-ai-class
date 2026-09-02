import os
import sys
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from core_agent import (
    get_chat_model,
    run_agent_turn,
    generate_voice_bytes,
    TOOLS,
    AVAILABLE_VOICES,
    FALLBACK_HEALTH_TOPICS
)

# ==========================================
# 1. Page Configuration & Custom Styling
# ==========================================

st.set_page_config(
    page_title="MedVoice AI - Autonomous Medical Voice Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern medical UI aesthetic
st.markdown("""
<style>
    /* Metric / card styling */
    .med-header {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(59, 130, 246, 0.08) 100%);
        border-radius: 12px;
        border: 1px solid rgba(14, 165, 233, 0.25);
        margin-bottom: 1.2rem;
    }
    .med-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: #0284c7;
    }
    .med-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        margin-top: 4px;
        margin-bottom: 0;
    }
    .disclaimer-box {
        background-color: rgba(245, 158, 11, 0.08);
        border-left: 4px solid #f59e0b;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #92400e;
        margin-bottom: 1.5rem;
    }
    .quick-chip {
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .tool-badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. Sidebar Configuration & API Key Management
# ==========================================

# Helper to fetch API key from st.secrets or os.getenv
def get_default_api_key() -> str:
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENROUTER_API_KEY", "")


with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=64)
    st.title("MedVoice AI")
    st.caption("NIH MedlinePlus Voice Assistant")
    st.divider()

    st.subheader("🔑 OpenRouter API Key")
    default_key = get_default_api_key()
    api_key_input = st.text_input(
        "Enter API Key",
        value=default_key,
        type="password",
        placeholder="sk-or-v1-...",
        help="Reads from secrets.toml, .env, or manual input."
    )

    if api_key_input:
        st.success("API Key Active", icon="🟢")
    else:
        st.warning("Please provide an OpenRouter API key.", icon="⚠️")

    st.divider()

    st.subheader("⚙️ Model & Voice Settings")
    
    model_options = [
        "nvidia/nemotron-3.5-lightning:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-001",
        "openai/gpt-4o-mini",
        "Custom..."
    ]
    
    selected_model = st.selectbox(
        "LLM Model",
        options=model_options,
        index=0,
        help="Select the OpenRouter model. Free tiers are supported."
    )
    
    if selected_model == "Custom...":
        active_model_name = st.text_input("Enter Model Identifier", value="nvidia/nemotron-3.5-lightning:free")
    else:
        active_model_name = selected_model

    temperature = st.slider(
        "Temperature (Creativity vs Factuality)",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Set to 0.0 for strict factual medical answers."
    )

    st.divider()

    st.subheader("🎙️ Speech Synthesis (Edge-TTS)")
    enable_voice = st.toggle("Enable Spoken Audio Response", value=True)

    selected_voice_label = st.selectbox(
        "Voice & Accent",
        options=list(AVAILABLE_VOICES.keys()),
        index=0,
        disabled=not enable_voice
    )
    active_voice_id = AVAILABLE_VOICES[selected_voice_label]

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    with st.expander("ℹ️ Architecture & Safety"):
        st.markdown("""
        **Pipeline Overview**:
        1. **LangChain Agent**: Evaluates user query.
        2. **MedlinePlus Tool**: Fetches verified health summaries from the NIH XML Search API.
        3. **Fallback Knowledge**: Built-in summaries for hypertension, asthma, diabetes, fever, and headache.
        4. **Safety Guardrails**: Non-diagnostic, non-prescriptive, spoken-friendly answers.
        5. **Edge-TTS**: High-quality neural speech synthesis rendered in-browser.
        """)


# ==========================================
# 3. Main Chat Interface
# ==========================================

# Header Banner
st.markdown("""
<div class="med-header">
    <div style="font-size: 2.4rem;">🩺</div>
    <div>
        <h1 class="med-title">MedVoice AI Assistant</h1>
        <p class="med-subtitle">Autonomous medical information agent powered by LangChain, NIH MedlinePlus & Neural Speech Synthesis</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Prominent Medical Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ Important Educational Disclaimer:</strong> This application is developed for <em>educational and research purposes only</em>. 
    It does not diagnose medical conditions, prescribe medicines, or replace professional medical evaluation. 
    Always seek the guidance of a qualified healthcare provider with any medical questions.
</div>
""", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your educational medical voice assistant. Ask me any health or medical topic, and I will retrieve trusted information from the National Library of Medicine (MedlinePlus) for you.",
            "tool_logs": [],
            "audio_bytes": None
        }
    ]

# Suggested Query Chips
st.markdown("**Common Health Topics:**")
col1, col2, col3, col4 = st.columns(4)
quick_prompt = None

with col1:
    if st.button("🩸 Hypertension Overview", use_container_width=True):
        quick_prompt = "Can you tell me about hypertension and how it is managed?"
with col2:
    if st.button("🌡️ Fever Symptoms & Care", use_container_width=True):
        quick_prompt = "What causes a fever and what is the home care advice?"
with col3:
    if st.button("🫁 Asthma Triggers & Care", use_container_width=True):
        quick_prompt = "What is asthma, what triggers it, and how is it managed?"
with col4:
    if st.button("🩺 Diabetes Overview", use_container_width=True):
        quick_prompt = "Can you explain diabetes in simple terms?"

# Render Past Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🩺" if msg["role"] == "assistant" else "👤"):
        # If tool calls were made, display an inspectable expander
        if msg.get("tool_logs"):
            for log in msg["tool_logs"]:
                with st.expander(f"🔍 MedlinePlus NIH Tool Search: '{log.get('args', {}).get('topic', 'topic')}'", expanded=False):
                    st.markdown(f"**Tool:** `{log.get('tool')}`")
                    st.markdown(f"**Parameters:** `{log.get('args')}`")
                    st.text_area("Retrieved NIH Medical Summary:", value=log.get("output", ""), height=130, disabled=True)

        st.markdown(msg["content"])

        # Display audio player if speech was generated
        if msg.get("audio_bytes"):
            st.audio(msg["audio_bytes"], format="audio/mp3")
            st.download_button(
                label="⬇️ Download Spoken Response (.mp3)",
                data=msg["audio_bytes"],
                file_name="medical_response.mp3",
                mime="audio/mp3",
                key=f"dl_{hash(msg['content'])}"
            )

# Handle User Input (from Chat Input or Quick Chips)
user_query = st.chat_input("Ask a health or medical question...")
if quick_prompt:
    user_query = quick_prompt

if user_query:
    if not api_key_input:
        st.error("Please provide an OpenRouter API key in the sidebar before asking questions.")
        st.stop()

    # Append user question to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_query,
        "tool_logs": [],
        "audio_bytes": None
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # Generate assistant answer
    with st.chat_message("assistant", avatar="🩺"):
        with st.status("Consulting MedlinePlus NIH Database & Synthesizing Response...", expanded=True) as status:
            try:
                # 1. Initialize Chat Model
                status.write(f"Connecting to model: `{active_model_name}`...")
                model = get_chat_model(active_model_name, api_key_input, temperature=temperature)
                model_with_tools = model.bind_tools(TOOLS)

                # 2. Run Agent Turn with Tool Calling
                status.write("Analyzing query & searching MedlinePlus XML API...")
                turn_result = run_agent_turn(model, model_with_tools, user_query)
                answer = turn_result["answer"]
                tool_logs = turn_result["tool_logs"]

                # 3. Voice Synthesis (if enabled)
                audio_bytes = None
                if enable_voice and answer:
                    status.write(f"Synthesizing neural voice audio using `{active_voice_id}`...")
                    audio_bytes = generate_voice_bytes(answer, voice=active_voice_id)

                status.update(label="Response generated successfully!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error processing query", state="error", expanded=True)
                st.error(f"Error: {e}")
                st.stop()

        # Render Tool Call Details
        if tool_logs:
            for log in tool_logs:
                with st.expander(f"🔍 MedlinePlus NIH Tool Search: '{log.get('args', {}).get('topic', 'topic')}'", expanded=False):
                    st.markdown(f"**Tool:** `{log.get('tool')}`")
                    st.markdown(f"**Parameters:** `{log.get('args')}`")
                    st.text_area("Retrieved NIH Medical Summary:", value=log.get("output", ""), height=130, disabled=True)

        # Render Final Answer
        st.markdown(answer)

        # Render Audio Player
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="⬇️ Download Spoken Response (.mp3)",
                data=audio_bytes,
                file_name="medical_response.mp3",
                mime="audio/mp3",
                key=f"dl_{hash(answer)}"
            )

        # Save assistant message to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "tool_logs": tool_logs,
            "audio_bytes": audio_bytes
        })
