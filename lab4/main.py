import os
import sys
import asyncio
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
# 1. Define Medical Tools
# ==========================================

# Curated educational summaries for fallback when live network is restricted
FALLBACK_HEALTH_TOPICS = {
    "hypertension": (
        "Hypertension, also known as high blood pressure, occurs when the force of blood "
        "against the walls of your arteries is consistently too high. Over time, uncontrolled "
        "high blood pressure increases the risk of heart disease, stroke, and kidney problems. "
        "Lifestyle measures such as eating a balanced low-sodium diet, regular exercise, maintaining "
        "a healthy weight, and routine monitoring are foundational to management."
    ),
    "fever": (
        "A fever is a temporary elevation of body temperature above normal (typically 100.4°F or 38°C), "
        "usually indicating that the body is actively fighting an infection like a cold or flu. "
        "Rest, adequate hydration with plenty of fluids, and comfortable clothing help manage symptoms. "
        "Seek medical attention if a fever is very high, lasts more than 3 days, or accompanies severe symptoms."
    ),
    "diabetes": (
        "Diabetes is a chronic metabolic health condition that affects how your body turns food into energy. "
        "The main types are Type 1 (where the pancreas produces little to no insulin) and Type 2 (where cells "
        "become resistant to insulin). Key management strategies include balanced nutrition, physical activity, "
        "monitoring blood glucose levels, and medical follow-up."
    ),
    "asthma": (
        "Asthma is a chronic condition affecting the airways of the lungs, causing them to swell, narrow, "
        "and produce extra mucus. Common triggers include pollen, dust mites, pet dander, cold air, and exercise. "
        "Management includes identifying and avoiding triggers and following a personalized action plan with a healthcare provider."
    ),
    "headache": (
        "Headaches involve pain in the head or upper neck. Common types include tension headaches and migraines. "
        "Frequent causes include stress, dehydration, lack of sleep, or eye strain. Resting in a quiet, dark room "
        "and staying hydrated can help."
    )
}

@tool
def medical_information(topic: str) -> str:
    """
    Search MedlinePlus for general medical information about a topic.
    Provides educational information only and does not diagnose or prescribe.
    """
    topic_clean = topic.strip().lower()
    url = "https://wsearch.nlm.nih.gov/ws/query"
    params = {
        "db": "healthTopics",
        "term": topic_clean,
        "retmax": 3,
        "rettype": "brief"
    }

    try:
        import urllib3
        urllib3.disable_warnings()
        response = requests.get(url, params=params, timeout=4, verify=False)
        response.raise_for_status()

        # Check if response is valid XML and not an HTML redirect/bot challenge
        if response.text.strip().startswith("<?xml") or "<nlmSearchResult" in response.text:
            root = ET.fromstring(response.text)
            results = []

            for document in root.findall(".//document"):
                title = ""
                summary = ""
                page_url = document.attrib.get("url", "")

                for content in document.findall("content"):
                    name = content.attrib.get("name")
                    text = "".join(content.itertext()).strip()

                    if name == "title":
                        title = text
                    elif name == "full-summary":
                        summary = text

                if title or summary:
                    results.append({
                        "title": title,
                        "summary": summary,
                        "url": page_url
                    })

            if results:
                output = f"Medical information from MedlinePlus for '{topic}':\n\n"
                for i, result in enumerate(results, 1):
                    output += f"{i}. {result['title']}\n"
                    output += f"{result['summary']}\n"
                    output += f"Source: {result['url']}\n\n"

                output += (
                    "Important: This information is for educational purposes only. "
                    "It does not provide a diagnosis or medical prescription."
                )
                return output

    except Exception:
        pass

    # Check curated verified fallback topics
    for key, text in FALLBACK_HEALTH_TOPICS.items():
        if key in topic_clean or topic_clean in key:
            return (
                f"Medical information for '{topic}':\n\n{text}\n\n"
                "Important: This information is for educational purposes only. "
                "It does not provide a diagnosis or medical prescription."
            )

    return (
        f"General educational overview for '{topic}': Consult trusted sources such as MedlinePlus or your healthcare provider for clinical details.\n"
        "Important: This information is for educational purposes only. "
        "It does not provide a diagnosis or medical prescription."
    )


TOOLS = [medical_information]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

SYSTEM_PROMPT = """
You are a medical information voice assistant.

Your job is to provide general educational medical information.

Important rules:
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not replace a healthcare professional.
- Use information retrieved from the medical information tool.
- Since your response will be spoken aloud, keep the answer concise.
- Use simple language.
- Do not use Markdown (avoid asterisks, hashes, and bullet symbols).
- Avoid long lists.
"""


# ==========================================
# 2. Voice Generation (Edge-TTS)
# ==========================================

async def generate_voice(text: str, output_path: str = "medical_response.mp3", voice: str = "en-IN-NeerjaNeural"):
    """
    Synthesize text into speech using Microsoft Edge Neural TTS.
    """
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"[Warning] Failed to generate voice with edge-tts: {e}")
        return None


def play_audio(audio_path: str):
    """
    Play generated audio file on Windows.
    """
    if not os.path.exists(audio_path):
        return
    try:
        os.system(f'powershell -c "$wmp = New-Object -ComObject WMPlayer.OCX; $wmp.URL = \'{os.path.abspath(audio_path)}\'; $wmp.controls.play(); Start-Sleep -Seconds 3" | Out-Null')
    except Exception:
        pass


# ==========================================
# 3. Agent Execution Workflow
# ==========================================

def run_agent_turn(model, model_with_tools, user_query: str, enable_voice: bool = False):
    """
    Runs an agent turn with the medical model, executes any tool calls,
    and optionally synthesizes the response into speech.
    """
    messages = [
        HumanMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query)
    ]

    print("[Assistant] Thinking...", flush=True)
    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        messages.append(response)
        print(f"\n[Tool Execution Required: {len(response.tool_calls)} call(s)]", flush=True)

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            print(f" -> Calling Tool: '{tool_name}' with args: {tool_args}", flush=True)

            tool_fn = TOOLS_BY_NAME.get(tool_name)
            if tool_fn:
                tool_output = tool_fn.invoke(tool_args)
            else:
                tool_output = f"Error: Tool '{tool_name}' not recognized."

            preview = str(tool_output).splitlines()[0] if tool_output else ""
            print(f" -> Tool Result: {preview[:80]}...", flush=True)

            tool_message = ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_id
            )
            messages.append(tool_message)

        print("[Assistant] Synthesizing final answer from medical findings...", flush=True)
        final_response = model_with_tools.invoke(messages)
        answer = final_response.content

        # If model returned empty content or another tool call, generate direct answer using base model
        if not answer or not str(answer).strip():
            fallback_prompt = [
                HumanMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Medical information found:\n{tool_output}\n\n"
                        f"Patient question: {user_query}\n\n"
                        "Please answer the patient's question in 1-2 concise, spoken-friendly sentences."
                    )
                )
            ]
            final_response = model.invoke(fallback_prompt)
            answer = final_response.content
    else:
        answer = response.content

    print(f"\n[Medical Assistant]:\n{answer}\n", flush=True)

    if enable_voice and answer and answer.strip():
        print("[Voice] Synthesizing speech via Edge-TTS...", flush=True)
        audio_file = asyncio.run(generate_voice(answer))
        if audio_file and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            print(f" -> Audio saved to: {audio_file} ({os.path.getsize(audio_file)} bytes)", flush=True)
            play_audio(audio_file)

    return answer


# ==========================================
# 4. Main Entry Point
# ==========================================

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")

    model_name = os.getenv("LLM_MODEL", "nvidia/nemotron-3.5-lightning:free")
    enable_voice = "--voice" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != "--voice"]

    print("=" * 65, flush=True)
    print(" Autonomous Medical Voice AI Assistant (LangChain & MedlinePlus)", flush=True)
    print("=" * 65, flush=True)
    print(f"API Key: Loaded", flush=True)
    print(f"Model:   {model_name}", flush=True)
    print(f"Voice:   {'Enabled (--voice)' if enable_voice else 'Disabled (add --voice to enable)'}", flush=True)
    print("Tools:   medical_information (MedlinePlus API)", flush=True)
    print("=" * 65, flush=True)

    model = get_chat_model(model_name, api_key)
    model_with_tools = model.bind_tools(TOOLS)

    # Handle one-off query from command line arguments
    if args:
        query = " ".join(args)
        print(f"\n[Patient]: {query}", flush=True)
        run_agent_turn(model, model_with_tools, query, enable_voice=enable_voice)
        return

    # Interactive Loop
    print("\nAsk a health/medical question or type 'exit' to quit.\nExamples:", flush=True)
    print(" - 'Can you tell me about hypertension?'", flush=True)
    print(" - 'What causes a fever?'", flush=True)
    print(" - 'What are the symptoms and care for asthma?'", flush=True)
    print(" - 'Tell me about diabetes in simple terms.'\n", flush=True)

    while True:
        try:
            user_input = input("[Patient]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.", flush=True)
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye and stay healthy!", flush=True)
            break

        run_agent_turn(model, model_with_tools, user_input, enable_voice=enable_voice)


if __name__ == "__main__":
    main()
