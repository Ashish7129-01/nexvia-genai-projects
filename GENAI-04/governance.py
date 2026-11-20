import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
from groq import Groq
st.set_page_config(
    page_title="AI Safety and Governance",
    page_icon="🛡️",
    layout="wide"
)
LOG_FILE = Path("governance_logs.jsonl")
DAILY_LIMIT = 50
GUARD_MODEL = "meta-llama/llama-guard-4-12b"
st.title("🛡️ AI Safety and Governance")
st.caption("Multimodal AI Studio — Safety Monitoring")
def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY")
        except (FileNotFoundError, KeyError):
            key = None
    return Groq(api_key=key) if key else None
def read_logs():
    if not LOG_FILE.exists():
        return []
    records = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
def save_log(status, category=""):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "category": category
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
def today_count(logs):
    today = datetime.now(timezone.utc).date().isoformat()
    return sum(
        1 for item in logs
        if item.get("timestamp", "").startswith(today)
        and item.get("status") in ("SAFE", "BLOCKED", "ERROR")
    )
logs = read_logs()
count = today_count(logs)
col1, col2, col3 = st.columns(3)
col1.metric("Requests Today", count)
col2.metric("Daily Demo Limit", DAILY_LIMIT)
col3.metric(
    "Blocked Requests",
    sum(1 for item in logs if item.get("status") == "BLOCKED")
)
st.divider()
st.subheader("🔍 AI Prompt Safety Checker")
prompt = st.text_area(
    "Enter a prompt to check",
    placeholder="Enter any AI prompt..."
)
if st.button("Check Safety"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    elif count >= DAILY_LIMIT:
        st.error("Daily demonstration request limit reached.")
    else:
        client = get_client()
        if not client:
            st.error("Groq API key not configured.")
        else:
            try:
                with st.spinner("Running Llama Guard..."):
                    result = client.chat.completions.create(
                        model=GUARD_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0,
                        max_tokens=100
                    )
                verdict = (
                    result.choices[0].message.content or ""
                ).strip().lower()
                if re.match(r"^unsafe\b", verdict):
                    st.error("🚫 Unsafe prompt detected")
                    st.write("Model category:", verdict)
                    save_log("BLOCKED", verdict)
                elif re.match(r"^safe\b", verdict):
                    st.success("✅ Prompt passed Llama Guard")
                    save_log("SAFE")
                else:
                    st.warning(
                        "Safety verdict could not be interpreted. "
                        "Request not approved."
                    )
                    save_log("ERROR", "UNKNOWN_VERDICT")
            except Exception as e:
                st.error(f"Safety service unavailable: {e}")
                save_log("ERROR", "SERVICE_FAILURE")
st.divider()
st.subheader("📊 Governance Activity Log")
logs = read_logs()
if logs:
    st.dataframe(
        list(reversed(logs[-100:])),
        use_container_width=True
    )
else:
    st.info("No governance activity recorded yet.")
st.caption(
    "Demo governance module. Logs are local and "
    "limits apply only to this module, not other AI endpoints."
)
