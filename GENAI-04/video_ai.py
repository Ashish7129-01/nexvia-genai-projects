import os
import tempfile
import cv2
import streamlit as st
from groq import Groq
st.set_page_config(
    page_title="AI Video Analysis",
    page_icon="🎬",
    layout="wide"
)
st.title("🎬 AI Video Analysis")
st.write("Multimodal AI Studio — Video Intelligence")
uploaded = st.file_uploader(
    "Upload a video",
    type=["mp4", "mov", "avi"]
)
if uploaded:
    st.video(uploaded)
    if st.button("Analyze Video"):
        path = None
        try:
            with st.spinner("Analyzing video..."):
                suffix = os.path.splitext(uploaded.name)[1]
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp:
                    temp.write(uploaded.getvalue())
                    path = temp.name
                cap = cv2.VideoCapture(path)
                if not cap.isOpened():
                    raise ValueError("Cannot open video.")
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(
                    cv2.CAP_PROP_FRAME_COUNT
                )
                duration = (
                    frame_count / fps if fps > 0 else 0
                )
                samples = []
                previous = None
                analyzed = 0
                while analyzed < 12:
                    success, frame = cap.read()
                    if not success:
                        break
                    gray = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2GRAY
                    )
                    brightness = float(gray.mean())
                    motion = 0.0
                    if previous is not None:
                        motion = float(
                            cv2.absdiff(
                                gray, previous
                            ).mean()
                        )
                    samples.append({
                        "brightness": round(brightness, 2),
                        "visual_change": round(motion, 2)
                    })
                    previous = gray
                    analyzed += 1
                cap.release()
                if not samples:
                    raise ValueError(
                        "No readable frames found."
                    )
                st.success("Video frames analyzed!")
                st.metric(
                    "Duration",
                    f"{duration:.2f} seconds"
                )
                st.metric(
                    "Frames sampled",
                    len(samples)
                )
                st.write("Visual measurements:")
                st.dataframe(samples)
                key = os.getenv("GROQ_API_KEY")
                if key:
                    client = Groq(api_key=key)
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Summarize video metadata "
                                    "and visual measurements. "
                                    "Do not claim to identify "
                                    "objects, people, or events "
                                    "because actual video frames "
                                    "are not provided."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Duration: {duration:.2f} "
                                    f"seconds. Measurements: "
                                    f"{samples}. Provide a short "
                                    "technical video summary."
                                )
                            }
                        ]
                    )
                    st.subheader("AI Video Summary")
                    st.write(
                        response.choices[0].message.content
                    )
                else:
                    st.warning(
                        "Groq API key not configured. "
                        "Local video analysis is available."
                    )
        except Exception as e:
            st.error(f"Video analysis failed: {e}")
        finally:
            if path and os.path.exists(path):
                os.remove(path)
