# Multimodal AI Studio with Safety and Governance Layer
## Project Overview
A Streamlit-based AI prototype supporting text, image, audio, and video workflows with basic safety and governance features.
## Features
- AI text generation using Groq
- AI image generation
- Speech-to-text transcription
- Text-to-speech generation
- Video metadata analysis with AI summaries
- Automatic text prompt safety checks
- Safety decision logging
- Unified navigation dashboard
## Technology Stack
Python, Streamlit, Groq API, OpenCV, Pillow, Requests
## How to Run
1. Install dependencies from requirements.txt.
2. Configure the GROQ_API_KEY environment variable.
3. Run the PowerShell launcher:
   .\start_project.ps1
4. Open http://localhost:8506
## Current Scope
This repository contains a working prototype. Next.js authentication, LiteLLM routing, and advanced governance features remain future improvements.
## Security
Never commit API keys, environment files, or local governance logs.
