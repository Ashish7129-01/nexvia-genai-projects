import os
import json
from datetime import datetime, timezone
import re
from groq import Groq
def check_prompt_safety(prompt):
    if not prompt or not prompt.strip():
        return False, "Empty prompt"
    try:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="openai/gpt-oss-safeguard-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a safety classifier. "
                        "Classify the user's request as SAFE or UNSAFE. "
                        "Return only the classification label."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_completion_tokens=100,
            reasoning_effort="low"
        )
        result = (response.choices[0].message.content or "").strip().upper()
        if re.fullmatch(r"SAFE[.!]?", result):
            log_safety_event(prompt, True, "Prompt passed AI safety check")
            return True, "Prompt passed AI safety check"
        if re.fullmatch(r"UNSAFE[.!]?", result):
            log_safety_event(prompt, False, "Unsafe prompt detected")
            return False, "Unsafe prompt detected"
        return False, "Safety classification unclear"
    except Exception:
        return False, "Safety service unavailable"

def log_safety_event(prompt, allowed, reason):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": "SAFE" if allowed else "BLOCKED",
        "reason": reason,
        "prompt_length": len(prompt)
    }
    with open("safety_events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
