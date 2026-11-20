 
import atexit
import uuid

from sentence_transformers import SentenceTransformer
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

# Existing Qdrant configuration
COLLECTION_NAME = "enterprise_documents"
VECTOR_SIZE = 384

# Initialize local Qdrant database

client = QdrantClient(
    path=str(Path(__file__).resolve().parent / "qdrant_storage")
)


# Close Qdrant during normal Python shutdown
atexit.register(client.close)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Create collection only if it does not exist
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


# Store document chunks in Qdrant
def store_chunks(chunks):
    if not chunks:
        return 0

    points = []

    for chunk in chunks:
        embedding = model.encode(chunk["text"]).tolist()

        # Preserve existing chunk metadata
        payload = dict(chunk)

        # New documents require explicit permissions.
        # Missing permissions default to no access.
        allowed_roles = payload.get("allowed_roles", [])

        if not isinstance(allowed_roles, list):
            allowed_roles = []

        payload["allowed_roles"] = [
            role
            for role in allowed_roles
            if role in ("admin", "employee")
        ]

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload,
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


# Semantic search with Qdrant-level RBAC
def search_chunks(query: str, limit: int = 5, user_role=None):
    # Deny missing or invalid roles
    if user_role not in ("admin", "employee"):
        return []

    query_vector = model.encode(query).tolist()

    role_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_roles",
                match=MatchValue(value=user_role),
            )
        ]
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=role_filter,
        limit=limit,
        with_payload=True,
    ).points

    return [
        {
            **(point.payload or {}),
            "score": point.score,
        }
        for point in results
    ]


# Retrieve all stored chunks

def get_all_chunks(user_role=None):
    # Deny missing or invalid roles
    if user_role not in ("admin", "employee"):
        return []

    role_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_roles",
                match=MatchValue(value=user_role)
            )
        ]
    )

    chunks = []
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=role_filter,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for point in points:
            chunks.append(point.payload or {})

        if offset is None:
            break

    return chunks

    chunks = []
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            chunks.append(point.payload or {})

        if offset is None:
            break

    return chunks
