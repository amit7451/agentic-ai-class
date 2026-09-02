"""
Core Medical Agent Module for Lab 4 Autonomous Medical Voice AI Assistant.
Preserves core LangChain tool-calling workflow, MedlinePlus NIH XML queries,
curated educational fallbacks, and Edge-TTS neural speech synthesis.
"""

import os
import sys
import asyncio
import io
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

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
# 1. Curated Fallback Health Knowledge Base
# ==========================================

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


# ==========================================
# 2. Medical Information Tool (MedlinePlus NIH)
# ==========================================

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

        if response.text.strip().startswith("<?xml") or "<nlmSearchResult" in response.text:
            root = ET.fromstring(response.text)
            results = []

            for document in root.findall(".//document"):
                title = ""
                summary = ""
                page_url = document.attrib.get("url", "")

                for content in document.findall("content"):
                    name = content.attrib.get("name")
                    raw_text = "".join(content.itertext()).strip()
                    import re
                    clean_text = re.sub(r"<[^>]+>", "", raw_text).strip()

                    if name == "title":
                        title = clean_text
                    elif name == "full-summary":
                        summary = clean_text

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
# 3. Voice Generation (Edge-TTS)
# ==========================================

AVAILABLE_VOICES = {
    "English (India) - Neerja (Female)": "en-IN-NeerjaNeural",
    "English (India) - Prabhat (Male)": "en-IN-PrabhatNeural",
    "English (US) - Jenny (Female)": "en-US-JennyNeural",
    "English (US) - Guy (Male)": "en-US-GuyNeural",
    "English (UK) - Sonia (Female)": "en-GB-SoniaNeural",
    "English (UK) - Ryan (Male)": "en-GB-RyanNeural"
}

async def _generate_voice_bytes_async(text: str, voice: str = "en-IN-NeerjaNeural") -> Optional[bytes]:
    """
    Generate MP3 audio bytes using Microsoft Edge Neural TTS.
    """
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=voice)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_bytes = audio_stream.getvalue()
        return audio_bytes if len(audio_bytes) > 0 else None
    except Exception as e:
        print(f"[Warning] Edge-TTS error: {e}", file=sys.stderr)
        return None


def generate_voice_bytes(text: str, voice: str = "en-IN-NeerjaNeural") -> Optional[bytes]:
    """
    Synchronous wrapper to generate audio bytes for Streamlit playback.
    """
    if not text or not text.strip():
        return None
    try:
        return asyncio.run(_generate_voice_bytes_async(text=text, voice=voice))
    except Exception as e:
        # Fallback to creating a new event loop if already in a loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_generate_voice_bytes_async(text=text, voice=voice))
            loop.close()
            return result
        except Exception as e2:
            print(f"[Warning] Failed to generate audio: {e2}", file=sys.stderr)
            return None


# ==========================================
# 4. Agent Turn Execution
# ==========================================

def run_agent_turn(model, model_with_tools, user_query: str) -> Dict[str, Any]:
    """
    Runs an agent turn with the medical model, executes any tool calls,
    and returns a dictionary containing the answer and tool execution logs.
    """
    messages = [
        HumanMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query)
    ]

    tool_logs: List[Dict[str, Any]] = []

    # Initial LLM call
    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        messages.append(response)

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            tool_fn = TOOLS_BY_NAME.get(tool_name)
            if tool_fn:
                tool_output = tool_fn.invoke(tool_args)
            else:
                tool_output = f"Error: Tool '{tool_name}' not recognized."

            tool_logs.append({
                "tool": tool_name,
                "args": tool_args,
                "output": str(tool_output)
            })

            tool_message = ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_id
            )
            messages.append(tool_message)

        # Synthesize final answer
        final_response = model_with_tools.invoke(messages)
        answer = final_response.content

        # Fallback prompt if answer is empty or repeated tool call
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

    return {
        "answer": str(answer).strip() if answer else "I am sorry, but I could not find information on that topic.",
        "tool_logs": tool_logs
    }
