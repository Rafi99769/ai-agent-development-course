# FastAPI Hello World with Google AI Embeddings

A FastAPI application with Google AI SDK integration for generating text embeddings using Google's text-embedding-004 model.

## Prerequisites

1. Get a Google AI API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

3. Add your API key to the `.env` file:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

## Setup

Install dependencies using UV:

```bash
uv sync
```

## Running the Application

### Option 1: Using the CLI command

```bash
uv run fastapi-hello
```

### Option 2: Using uvicorn directly

```bash
uv run uvicorn fastapi_hello.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## API Endpoints

### Basic Endpoints
- `GET /` - Hello World endpoint
- `GET /health` - Health check endpoint

### Text Embeddings Endpoint
- `POST /embeddings` - Generate text embeddings using Gemini's text-embedding-004 model

#### Request Body
```json
{
  "text": "Your text to embed"
}
```

#### Response
```json
{
  "text": "Your text to embed",
  "embedding": [0.123, -0.456, ...],
  "dimensions": 768
}
```

#### Example using curl
```bash
curl -X POST "http://localhost:8000/embeddings" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test sentence for embedding generation."}'
```

#### Example using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/embeddings",
    json={"text": "Hello, this is a test sentence for embedding generation."}
)

data = response.json()
print(f"Text: {data['text']}")
print(f"Embedding dimensions: {data['dimensions']}")
print(f"First 5 values: {data['embedding'][:5]}")
```

### PDF Embeddings Endpoint
- `POST /embeddings/pdf` - Upload a PDF file and generate embeddings for its text content

#### Request
Upload a PDF file using multipart/form-data

#### Response
```json
{
  "filename": "document.pdf",
  "text_preview": "First 200 characters of extracted text...",
  "total_characters": 5432,
  "embedding": [0.123, -0.456, ...],
  "dimensions": 768
}
```

#### Example using curl
```bash
curl -X POST "http://localhost:8000/embeddings/pdf" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/document.pdf"
```

#### Example using Python
```python
import requests

with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/embeddings/pdf",
        files={"file": ("document.pdf", f, "application/pdf")}
    )

data = response.json()
print(f"Filename: {data['filename']}")
print(f"Text preview: {data['text_preview']}")
print(f"Total characters extracted: {data['total_characters']}")
print(f"Embedding dimensions: {data['dimensions']}")
print(f"First 5 values: {data['embedding'][:5]}")
```

#### Features
- Extracts text from all pages of the PDF
- Validates file type (only .pdf files accepted)
- Handles empty PDFs or image-only PDFs with appropriate error messages
- Returns a preview of extracted text for verification
- Generates embeddings for the complete extracted text

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Google GenAI SDK**: Official Python SDK for Google's generative AI models
- **text-embedding-004**: Google's latest text embedding model
- **PyMuPDF (fitz)**: Fast and reliable PDF text extraction library
- **UV**: Fast Python package manager

## Project Structure

```
.
├── src/
│   └── fastapi_hello/
│       ├── __init__.py    # Package initialization and CLI entry point
│       └── main.py        # FastAPI application with endpoints
├── .env.example           # Example environment variables
├── pyproject.toml         # Project configuration and dependencies
└── README.md             # This file
```

## Notes

- The `text-embedding-004` model generates 768-dimensional embeddings by default
- Embeddings are useful for semantic search, similarity comparison, and RAG applications
- Make sure to keep your API key secure and never commit it to version control
- PDF text extraction works best with text-based PDFs; image-based or scanned PDFs may require OCR
- Large PDFs may take longer to process due to text extraction and embedding generation
