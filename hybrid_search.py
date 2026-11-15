 
import re
from rank_bm25 import BM25Plus


# Step 1: Tokenize text
def tokenize(text):
    return re.findall(r"\w+", text.lower())


# Step 2: BM25 keyword search
def bm25_search(query, chunks, limit=5):
    if not chunks:
        return []

    tokenized_corpus = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    bm25 = BM25Plus(tokenized_corpus)
    scores = bm25.get_scores(tokenize(query))

    ranked_indices = sorted(
        range(len(chunks)),
        key=lambda i: scores[i],
        reverse=True
    )

    return [
        {
            **chunks[i],
            "bm25_score": float(scores[i])
        }
        for i in ranked_indices[:limit]
    ]


# Step 3: Hybrid search with RBAC metadata
def hybrid_search(query, limit=5, user_role=None):
    from vector_store import search_chunks, get_all_chunks

    chunks = get_all_chunks(user_role=user_role)

    if not chunks:
        return []

    # Apply permissions before retrieval and ranking.
    # A missing role means no document access.
    from access_control import filter_documents_by_role

    chunks = filter_documents_by_role(chunks, user_role)

    if not chunks:
        return []

    # Semantic search currently searches the full collection.
    # Only authorized results are retained below.
        # Qdrant filters semantic results by user role
    semantic_results = search_chunks(
        query,
        limit=len(chunks),
        user_role=user_role
    )
    authorized_keys = {
        (chunk["source"], chunk["page"], chunk["text"])
        for chunk in chunks
    }

    semantic_results = [
        item
        for item in semantic_results
        if (
            item["source"],
            item["page"],
            item["text"]
        ) in authorized_keys
    ]

    keyword_results = bm25_search(
        query,
        chunks,
        limit=len(chunks)
    )

    # Create lookup for document permissions
    chunk_lookup = {
        (chunk["source"], chunk["page"], chunk["text"]): chunk
        for chunk in chunks
    }

    # Step 4: Reciprocal Rank Fusion
    combined = {}

    for results in [semantic_results, keyword_results]:
        for rank, item in enumerate(results, start=1):
            key = (
                item["source"],
                item["page"],
                item["text"]
            )

            if key not in chunk_lookup:
                continue

            if key not in combined:
                combined[key] = {
                    **chunk_lookup[key],
                    "rrf_score": 0.0,
                }

            combined[key]["rrf_score"] += 1.0 / (60 + rank)

    return sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )[:limit]
