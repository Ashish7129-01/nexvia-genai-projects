 
from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    Depends,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ingestion import process_document
from vector_store import store_chunks
from rag_pipeline import run_rag_pipeline

from users import authenticate_user, load_users
from auth import create_access_token, decode_access_token


# FastAPI application
app = FastAPI(
    title="Enterprise RAG Knowledge Platform",
    version="0.6.0",
)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

bearer_scheme = HTTPBearer(auto_error=False)


# Request models
class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class LoginRequest(BaseModel):
    username: str
    password: str


# JWT authentication
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload["sub"]

    users = load_users()
    user = users.get(username)

    if not user or user.get("role") != payload["role"]:
        raise HTTPException(
            status_code=401,
            detail="User account is invalid or permissions changed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "username": username,
        "role": user["role"],
    }


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Enterprise RAG Knowledge Platform is running!",
        "status": "success",
    }


# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# Admin-protected document upload
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):

    # Only administrators can upload documents
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can upload documents.",
        )

    filename = Path(file.filename or "").name

    # Validate file type
    if Path(filename).suffix.lower() not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    # Read uploaded file
    content = await file.read(10 * 1024 * 1024 + 1)

    # Check file size
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Process document
    try:
        chunks = process_document(content, filename)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process document: {exc}",
        ) from exc

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="No extractable text found.",
        )

    # Assign access permissions to uploaded chunks
    # Admin-only by default, until explicit sharing is added.
    for chunk in chunks:
        chunk["allowed_roles"] = ["admin"]

    # Store document
    destination = RAW_DIR / filename
    destination.write_bytes(content)

    # Store vectors in Qdrant
    stored_count = store_chunks(chunks)

    return {
        "message": "Document processed successfully",
        "filename": filename,
        "total_chunks": len(chunks),
        "vectors_stored": stored_count,
        "allowed_roles": ["admin"],
        "chunks": chunks[:3],
    }


# JWT-protected RAG chatbot
@app.post("/ask")
def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):

    try:
        answer = run_rag_pipeline(
            query=request.question,
            user_role=current_user["role"],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not generate an answer.",
        ) from exc

    return {
        "question": request.question,
        "answer": answer,
    }


# Login endpoint
@app.post("/login")
def login(request: LoginRequest):

    user = authenticate_user(
        request.username,
        request.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    try:
        token = create_access_token(
            username=user["username"],
            role=user["role"],
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured.",
        ) from exc

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
    }
