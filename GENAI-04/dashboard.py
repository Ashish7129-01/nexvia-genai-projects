import streamlit as st
st.set_page_config(
    page_title="Multimodal AI Studio",
    page_icon="🤖",
    layout="wide"
)
st.title("🤖 Multimodal AI Studio")
st.caption("Unified AI Platform with Safety and Governance")
st.success("Multimodal AI Studio — Modules Ready")
st.info(
    "Select a module below. Each module opens in a separate "
    "browser tab."
)
modules = [
    ("📝 Text, Image, Audio & Video", "http://localhost:8501"),
    ("🔊 Text-to-Speech", "http://localhost:8502"),
    ("🎬 AI Video Analysis", "http://localhost:8503"),
    ("🛡️ Safety & Governance", "http://localhost:8505"),
]
for name, url in modules:
    st.link_button(name, url, use_container_width=True)
st.divider()
st.caption("© 2026 Multimodal AI Studio")
