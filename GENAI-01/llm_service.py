import os
from groq import Groq


def generate_answer(query, documents):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    if not documents:
        return "I don't know based on the uploaded documents."

    client = Groq(api_key=api_key)

    context = "\n\n".join(
        f"[Source {i}] File: {doc.get('source', 'Unknown')}, "
        f"Page: {doc.get('page', 'Unknown')}\n"
        f"{doc.get('text', '')}"
        for i, doc in enumerate(documents, start=1)
    )

    prompt = f"""
You are an Enterprise RAG assistant.

Answer the question using ONLY the provided document context.

Rules:
1. Do not invent information.
2. Cite supporting sources using [Source 1], [Source 2], etc.
3. If the context does not contain the answer, say:
   "I don't know based on the uploaded documents."

Document context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {
                "role": "system",
                "content": "You answer questions using document evidence only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
