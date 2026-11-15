from sentence_transformers import CrossEncoder

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker_model = None


def rerank_results(query, documents, top_k=3):
    global reranker_model

    if not documents:
        return []

    if reranker_model is None:
        reranker_model = CrossEncoder(RERANKER_MODEL)

    pairs = [
        (query, document["text"])
        for document in documents
    ]

    scores = reranker_model.predict(pairs)

    ranked_documents = []

    for document, score in zip(documents, scores):
        ranked_documents.append({
            **document,
            "rerank_score": float(score)
        })

    ranked_documents.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    return ranked_documents[:top_k]
