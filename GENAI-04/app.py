import os
import re
from datetime import datetime
from urllib.parse import quote
from io import BytesIO

import requests
import streamlit as st
from groq import Groq
from PIL import Image

st.set_page_config(
    page_title="Multimodal AI Studio",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
h1, h2, h3 {
    color: #7c83ff;
}
div.stButton > button {
    background-color: #6366f1;
    color: white;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)


def get_api_key():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY")
        except (FileNotFoundError, KeyError):
            pass
    return key


def get_client():
    key = get_api_key()
    return Groq(api_key=key) if key else None


def is_safe_prompt(prompt):
    blocked_patterns = [
        r"\bmake\s+(a\s+)?bomb\b",
        r"\bhow\s+to\s+kill\b",
        r"\bsteal\s+(a\s+)?password\b",
    ]
    return not any(
        re.search(pattern, prompt, re.IGNORECASE)
        for pattern in blocked_patterns
    )


def log_event(feature, status):
    st.session_state.setdefault("events", [])
    st.session_state.events.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "feature": feature,
        "status": status
    })


st.title("🤖 Multimodal AI Studio")
st.write("AI-powered content creation with Safety and Governance")

with st.sidebar:
    st.header("⚙️ Control Panel")
    st.success("System Initialized")
    st.write("Version: 1.1.0")
    st.write("Date:", datetime.now().strftime("%d-%m-%Y"))
    st.divider()
    st.subheader("🛡️ Governance")
    st.write("Basic prompt filtering: Enabled")
    st.write("Advanced safety checks: Not configured")
    st.write("Budget tracking: Not configured")

    with st.expander("Activity Log"):
        for event in st.session_state.get("events", [])[-10:]:
            st.write(
                f"{event['time']} | "
                f"{event['feature']} | "
                f"{event['status']}"
            )

text_tab, image_tab, audio_tab, video_tab = st.tabs([
    "📝 Text AI",
    "🎨 Image AI",
    "🎤 Audio AI",
    "🎬 Video AI"
])

with text_tab:
    st.header("Text Generation")
    prompt = st.text_area("Enter your prompt")

    if st.button("Generate Text"):
        if prompt.strip():
            from safety_guard import check_prompt_safety
            safe, reason = check_prompt_safety(prompt)
            if not safe:
                st.error(reason)
                st.stop()
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        elif not is_safe_prompt(prompt):
            st.error("Prompt blocked by basic safety filter.")
            log_event("Text AI", "Blocked")
        else:
            client = get_client()

            if not client:
                st.error("GROQ_API_KEY is not configured.")
            else:
                try:
                    with st.spinner("Generating response..."):
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )

                    answer = response.choices[0].message.content
                    st.success("AI response generated!")
                    st.write(answer)
                    log_event("Text AI", "Success")

                except Exception as e:
                    st.error(f"Text generation failed: {e}")
                    log_event("Text AI", "Failed")

with image_tab:
    st.header("AI Image Generation")

    image_prompt = st.text_area(
        "Describe your image",
        placeholder="A futuristic city at sunset"
    )

    if st.button("Generate Image"):
        if not image_prompt.strip():
            st.warning("Please enter an image description.")
        elif not is_safe_prompt(image_prompt):
            st.error("Prompt blocked by basic safety filter.")
            log_event("Image AI", "Blocked")
        else:
            try:
                with st.spinner("Generating image..."):
                    url = (
                        "https://image.pollinations.ai/prompt/"
                        + quote(image_prompt, safe="")
                    )
                    result = requests.get(url, timeout=60)
                    result.raise_for_status()

                    if not result.headers.get(
                        "Content-Type", ""
                    ).startswith("image/"):
                        raise ValueError(
                            "Image service did not return an image."
                        )

                    image_bytes = result.content
                    image = Image.open(BytesIO(image_bytes))
                    image.load()

                st.image(image, caption="AI Generated Image")
                st.download_button(
                    "Download Image",
                    data=image_bytes,
                    file_name="generated_image.png",
                    mime=result.headers.get(
                        "Content-Type", "image/png"
                    )
                )
                log_event("Image AI", "Success")

            except Exception as e:
                st.error(f"Image generation failed: {e}")
                st.info(
                    "The public image service may be unavailable "
                    "or may require authentication."
                )
                log_event("Image AI", "Failed")

with audio_tab:
    st.header("Audio AI Studio")
    st.subheader("Speech to Text")

    audio_file = st.file_uploader(
        "Upload audio",
        type=["mp3", "wav", "m4a"]
    )

    if audio_file:
        st.audio(audio_file)

        if st.button("Transcribe Audio"):
            client = get_client()

            if not client:
                st.error("GROQ_API_KEY is not configured.")
            else:
                try:
                    with st.spinner("Transcribing audio..."):
                        transcription = (
                            client.audio.transcriptions.create(
                                file=(
                                    audio_file.name,
                                    audio_file.getvalue()
                                ),
                                model="whisper-large-v3-turbo"
                            )
                        )

                    st.success("Transcription completed!")
                    st.write(transcription.text)
                    log_event("Audio AI", "Success")

                except Exception as e:
                    st.error(f"Transcription failed: {e}")
                    log_event("Audio AI", "Failed")

with video_tab:
    st.header("Video AI Studio")

    video_file = st.file_uploader(
        "Upload video",
        type=["mp4", "mov", "avi"]
    )

    if video_file:
        st.video(video_file)
        st.info(
            "Video playback is ready. "
            "AI video processing is not yet connected."
        )

st.divider()
st.caption(
    "© 2026 Multimodal AI Studio | Safety & Governance Layer"
)
