# Enterprise RAG Knowledge Platform

## Project Overview

The Enterprise RAG Knowledge Platform is a Python-based document question-answering system using Retrieval-Augmented Generation (RAG).

The platform allows authorized users to ask questions about uploaded enterprise documents and receive AI-generated answers with source citations.

## Technologies Used

- **Backend:** Python, FastAPI
- **Document Processing:** PDF and DOCX ingestion
- **Embeddings:** Sentence Transformers
- **Vector Database:** Qdrant
- **Keyword Retrieval:** BM25
- **Search Strategy:** Hybrid retrieval with reciprocal rank fusion
- **Reranking:** Cross-Encoder
- **LLM:** Groq API
- **Authentication:** JWT
- **Access Control:** Administrator and Employee roles

## Key Features

1. PDF and DOCX document processing
2. Document chunking and vector embeddings
3. Qdrant vector storage
4. Hybrid semantic and keyword search
5. Cross-encoder reranking
6. AI-generated answers with source citations
7. JWT-based user authentication
8. Role-based document access
9. Administrator-only document uploads
10. REST API documentation using Swagger UI

## System Workflow

Document Upload → Text Extraction → Chunking → Embeddings → Qdrant Storage

User Login → JWT Authentication → Question → Role-Based Hybrid Retrieval → Reranking → LLM → Answer with Citations

## Installation

Requires Python 3.12 and the dependencies listed in `requirements.txt`.

```powershell
python -m pip install -r requirements.txt
```

## Running the Application

Configure the `GROQ_API_KEY` and `JWT_SECRET_KEY` environment variables before starting the application.

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open Swagger UI:

http://127.0.0.1:8000/docs

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Application status |
| `/health` | GET | Health check |
| `/login` | POST | Authenticate user and issue JWT |
| `/documents/upload` | POST | Administrator-only document upload |
| `/ask` | POST | Authenticated document question answering |

## Security

The application uses JWT authentication and role-based access control.

- Administrators can upload documents.
- Employees can query documents permitted for their role.
- Uploaded documents are administrator-only by default.
- Passwords are stored as hashes rather than plaintext.

This is a local development prototype. Production deployment requires additional security hardening.

## Testing

The following checks have been performed during development:

- Python syntax and module import checks
- Employee and administrator authentication
- Unauthenticated upload rejection
- Employee upload restriction
- Administrator PDF upload
- Role-based Qdrant retrieval
- RAG answer generation with source citations

## Future Improvements

- Web-based chatbot interface
- Administrator-controlled document sharing
- Retrieval quality evaluation dashboard
- Persistent secret management
- Audit logging and deployment hardening

## Project Status

Core implementation completed and tested. Final integration verification and deployment preparation remain.