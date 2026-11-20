 
from hybrid_search import hybrid_search
from reranker import rerank_results
from llm_service import generate_answer
from access_control import filter_documents_by_role


def run_rag_pipeline(query, user_role="employee"):
    """
    Run the Enterprise RAG pipeline with
    role-based document filtering.
    """

    # Step 1: Retrieve permitted document chunks
    retrieved_docs = hybrid_search(
        query,
        limit=5,
        user_role=user_role
    )

    if not retrieved_docs:
        return "I don't know based on the uploaded documents."

    # Step 2: Apply role-based document filtering
    # Additional safeguard before sending data to the LLM
    authorized_docs = filter_documents_by_role(
        retrieved_docs,
        user_role
    )

    if not authorized_docs:
        return "I don't know based on the uploaded documents."

    # Step 3: Rerank authorized documents
    ranked_docs = rerank_results(
        query,
        authorized_docs,
        top_k=3
    )

    if not ranked_docs:
        return "I don't know based on the uploaded documents."

    # Step 4: Recheck permissions after reranking
    ranked_docs = filter_documents_by_role(
        ranked_docs,
        user_role
    )

    if not ranked_docs:
        return "I don't know based on the uploaded documents."

    # Step 5: Generate an answer with citations
    answer = generate_answer(
        query,
        ranked_docs
    )

    return answer
