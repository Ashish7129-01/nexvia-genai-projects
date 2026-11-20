import os
import streamlit as st
from groq import Groq
st.set_page_config(page_title="AI Text-to-Speech", page_icon="🔊")
st.title("🔊 AI Text-to-Speech")
st.write("Multimodal AI Studio — Voice Generation")
text = st.text_area(
    "Enter text to convert into speech",
    value="Hello! Welcome to Multimodal AI Studio."
)
voice = st.selectbox(
    "Select voice",
    ["troy", "diana", "hannah", "autumn", "austin"]
)
if st.button("Generate Speech"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            st.error("Groq API key is not configured.")
        else:
            try:
                client = Groq(api_key=key)
                with st.spinner("Generating speech..."):
                    response = client.audio.speech.create(
                        model="canopylabs/orpheus-v1-english",
                        voice=voice,
                        input=text,
                        response_format="wav"
                    )
                    audio_bytes = response.read()
                st.success("Speech generated successfully!")
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    "Download Speech",
                    data=audio_bytes,
                    file_name="generated_speech.wav",
                    mime="audio/wav"
                )
            except Exception as e:
                st.error(f"Speech generation failed: {e}")
