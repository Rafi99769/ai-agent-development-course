# DIY Guide: Building a FastAPI Application with Google AI Embeddings

## 📚 What You'll Learn

In this class, you'll build a **FastAPI web application** that can:
- Create a REST API with multiple endpoints
- Generate text embeddings using Google's AI models
- Extract text from PDF files and create embeddings
- Calculate similarity between texts

**What are embeddings?** Embeddings are numerical representations of text that capture meaning. Similar texts have similar embeddings, making them useful for search, recommendations, and AI applications.

---

## 🎯 Prerequisites

Before starting, make sure you have:
1. **Python 3.10 or higher** installed on your computer
2. **UV package manager** installed ([Install UV](https://docs.astral.sh/uv/getting-started/installation/))
3. A **Google AI API key** (we'll get this in Step 1)
4. A code editor (VS Code, PyCharm, or any text editor)

---

## 📋 Step-by-Step Guide

### Step 1: Get Your Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key (you'll need it later)
5. **Keep it secret!** Never share your API key publicly

---

### Step 2: Create Your Project Structure

Open your terminal and create the project folders:

```bash
# Create the main project folder
mkdir fastapi-hello
cd fastapi-hello

# Create the source code structure
mkdir -p src/fastapi_hello

# Create necessary files
touch src/fastapi_hello/__init__.py
touch src/fastapi_hello/main.py
touch pyproject.toml
touch .env.example
touch .env
touch README.md
```

Your project structure should look like this:
```
fastapi-hello/
├── src/
│   └── fastapi_hello/
│       ├── __init__.py
│       └── main.py
├── .env.example
├── .env
├── pyproject.toml
└── README.md
```

---

### Step 3: Configure Your Project (pyproject.toml)

Open `pyproject.toml` and paste this configuration:

```toml
[project]
name = "fastapi-hello"
version = "0.1.0"
description = "FastAPI application with Google AI embeddings"
readme = "README.md"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.119.1",
    "genkit>=0.4.0",
    "genkit-plugin-google-genai>=0.4.0",
    "numpy>=1.26.0",
    "pymupdf>=1.26.5",
    "python-dotenv>=1.1.1",
    "python-multipart>=0.0.20",
    "scikit-learn>=1.3.0",
    "uvicorn>=0.38.0",
]

[project.scripts]
fastapi-hello = "fastapi_hello:main"

[build-system]
requires = ["uv_build>=0.8.4,<0.9.0"]
build-backend = "uv_build"
```

**What this does:**
- Defines your project name and version
- Lists all the libraries your project needs
- Creates a command `fastapi-hello` to run your app

---

### Step 4: Set Up Environment Variables

#### Create `.env.example` file:

```bash
# Google AI API Key for Gemini models
# Get your API key from: https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_api_key_here
```

#### Create `.env` file with your actual API key:

```bash
# Replace 'your_actual_api_key_here' with the API key you got in Step 1
GOOGLE_API_KEY=your_actual_api_key_here
```

**Important:** The `.env` file contains your secret API key. Never commit it to Git!

---

### Step 5: Write the Application Code

#### 5.1 Create `src/fastapi_hello/__init__.py`

This file makes your folder a Python package and provides a way to run the app:

```python
from fastapi_hello.main import app

__all__ = ["app"]


def main() -> None:
    """Entry point for running the FastAPI application."""
    import uvicorn
    uvicorn.run("fastapi_hello.main:app", host="0.0.0.0", port=8000, reload=True)
```

**What this does:**
- Imports the FastAPI app
- Creates a `main()` function that starts the web server
- Configures the server to run on port 8000 with auto-reload

---

#### 5.2 Create `src/fastapi_hello/main.py`

This is the main application file. Copy and paste this code:

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
from typing import Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="FastAPI Hello World", version="0.1.0")

# Initialize Google GenAI client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    text: str


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    text: str
    embedding: list[float]
    dimensions: int


class PDFEmbeddingResponse(BaseModel):
    """Response model for PDF embedding generation."""
    filename: str
    text_preview: str
    total_characters: int
    embedding: list[float]
    dimensions: int


class SimilarityRequest(BaseModel):
    """Request model for similarity calculation."""
    query_text: str
    candidate_texts: list[str]
    task_type: Optional[str] = "SEMANTIC_SIMILARITY"


class SimilarityScore(BaseModel):
    """Model for individual similarity score."""
    text: str
    similarity: float


class SimilarityResponse(BaseModel):
    """Response model for similarity calculation."""
    query_text: str
    task_type: str
    similarities: list[SimilarityScore]


@app.get("/")
async def root():
    """Root endpoint returning a hello world message."""
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """Generate embeddings for the input text using Gemini's text-embedding-004 model.
    
    Args:
        request: EmbeddingRequest containing the text to embed
        
    Returns:
        EmbeddingResponse with the original text, embedding vector, and dimensions
        
    Raises:
        HTTPException: If embedding generation fails
    """
    try:
        # Generate embeddings using Google GenAI's text-embedding-004 model
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=request.text,
        )
        
        # Extract the embedding values from the response
        embedding_values = result.embeddings[0].values
        
        return EmbeddingResponse(
            text=request.text,
            embedding=embedding_values,
            dimensions=len(embedding_values)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@app.post("/embeddings/pdf", response_model=PDFEmbeddingResponse)
async def generate_pdf_embeddings(file: UploadFile = File(...)):
    """Generate embeddings for a PDF file using Gemini's text-embedding-004 model.
    
    This endpoint:
    1. Accepts a PDF file upload
    2. Extracts all text from the PDF
    3. Generates embeddings for the extracted text
    4. Returns the embeddings along with metadata
    
    Args:
        file: PDF file to process
        
    Returns:
        PDFEmbeddingResponse with filename, text preview, embedding vector, and dimensions
        
    Raises:
        HTTPException: If file processing or embedding generation fails
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read the PDF file
        pdf_content = await file.read()
        
        # Extract text from PDF using PyMuPDF
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Extract text from all pages
        extracted_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            extracted_text += page.get_text()
        
        pdf_document.close()
        
        # Check if text was extracted
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF. The file might be empty or contain only images."
            )
        
        # Generate embeddings using Google GenAI's text-embedding-004 model
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=extracted_text,
        )
        
        # Extract the embedding values from the response
        embedding_values = result.embeddings[0].values
        
        # Create a preview of the extracted text (first 200 characters)
        text_preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        
        return PDFEmbeddingResponse(
            filename=file.filename,
            text_preview=text_preview,
            total_characters=len(extracted_text),
            embedding=embedding_values,
            dimensions=len(embedding_values)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF and generate embeddings: {str(e)}"
        )


@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """Calculate cosine similarity between a query text and a list of candidate texts.
    
    This endpoint:
    1. Accepts a query text and a list of candidate texts
    2. Generates embeddings for all texts using Gemini's embedding model
    3. Calculates cosine similarity between the query and each candidate
    4. Returns similarity scores for each candidate text
    
    Args:
        request: SimilarityRequest containing query_text, candidate_texts, and optional task_type
        
    Returns:
        SimilarityResponse with query text, task type, and similarity scores for each candidate
        
    Raises:
        HTTPException: If embedding generation or similarity calculation fails
    """
    # Validate task type
    valid_task_types = [
        "SEMANTIC_SIMILARITY", "CLASSIFICATION", "CLUSTERING",
        "RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY", "CODE_RETRIEVAL_QUERY",
        "QUESTION_ANSWERING", "FACT_VERIFICATION"
    ]
    
    if request.task_type not in valid_task_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_type. Must be one of: {', '.join(valid_task_types)}"
        )
    
    # Validate candidate texts
    if not request.candidate_texts:
        raise HTTPException(
            status_code=400,
            detail="candidate_texts cannot be empty"
        )
    
    try:
        # Combine query and candidate texts for batch embedding
        all_texts = [request.query_text] + request.candidate_texts
        
        # Generate embeddings for all texts
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=all_texts,
            config=types.EmbedContentConfig(task_type=request.task_type)
        )
        
        # Extract embeddings as numpy arrays
        embeddings = [np.array(e.values) for e in result.embeddings]
        
        # First embedding is the query, rest are candidates
        query_embedding = embeddings[0].reshape(1, -1)
        candidate_embeddings = np.array(embeddings[1:])
        
        # Calculate cosine similarity between query and each candidate
        similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
        
        # Create response with similarity scores
        similarity_scores = [
            SimilarityScore(
                text=text,
                similarity=float(score)
            )
            for text, score in zip(request.candidate_texts, similarities)
        ]
        
        return SimilarityResponse(
            query_text=request.query_text,
            task_type=request.task_type,
            similarities=similarity_scores
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate similarity: {str(e)}"
        )
```

---

### Step 6: Install Dependencies

Now install all the required libraries using UV:

```bash
uv sync
```

**What this does:**
- Reads your `pyproject.toml` file
- Downloads and installs all required packages
- Creates a virtual environment for your project

This may take a few minutes. Wait for it to complete.

---

### Step 7: Run Your Application

Start your FastAPI server:

```bash
uv run fastapi-hello
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Your API is now running!** 🎉

---

## 🧪 Testing Your API

### Test 1: Hello World Endpoint

Open your browser and go to:
```
http://localhost:8000
```

You should see:
```json
{"message": "Hello World"}
```

---

### Test 2: Interactive API Documentation

FastAPI automatically creates interactive documentation. Open:
```
http://localhost:8000/docs
```

You'll see a beautiful interface where you can test all your endpoints!

---

### Test 3: Generate Text Embeddings

#### Using curl (Terminal):

```bash
curl -X POST "http://localhost:8000/embeddings" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test sentence for embedding generation."}'
```

#### Using Python:

Create a file called `test_embeddings.py`:

```python
import requests

# Test text embeddings
response = requests.post(
    "http://localhost:8000/embeddings",
    json={"text": "Hello, this is a test sentence for embedding generation."}
)

data = response.json()
print(f"Text: {data['text']}")
print(f"Embedding dimensions: {data['dimensions']}")
print(f"First 5 values: {data['embedding'][:5]}")
```

Run it:
```bash
python test_embeddings.py
```

---

### Test 4: Upload PDF and Generate Embeddings

#### Using curl:

```bash
curl -X POST "http://localhost:8000/embeddings/pdf" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/document.pdf"
```

Replace `/path/to/your/document.pdf` with the actual path to a PDF file on your computer.

#### Using Python:

Create a file called `test_pdf.py`:

```python
import requests

# Replace with your PDF file path
pdf_path = "document.pdf"

with open(pdf_path, "rb") as f:
    response = requests.post(
        "http://localhost:8000/embeddings/pdf",
        files={"file": (pdf_path, f, "application/pdf")}
    )

data = response.json()
print(f"Filename: {data['filename']}")
print(f"Text preview: {data['text_preview']}")
print(f"Total characters extracted: {data['total_characters']}")
print(f"Embedding dimensions: {data['dimensions']}")
print(f"First 5 embedding values: {data['embedding'][:5]}")
```

Run it:
```bash
python test_pdf.py
```

---

### Test 5: Calculate Text Similarity

#### Using Python:

Create a file called `test_similarity.py`:

```python
import requests

# Test similarity calculation
response = requests.post(
    "http://localhost:8000/similarity",
    json={
        "query_text": "I love programming",
        "candidate_texts": [
            "I enjoy coding",
            "I like to eat pizza",
            "Programming is fun",
            "The weather is nice today"
        ]
    }
)

data = response.json()
print(f"Query: {data['query_text']}\n")
print("Similarity scores:")
for item in data['similarities']:
    print(f"  '{item['text']}' -> {item['similarity']:.4f}")
```

Run it:
```bash
python test_similarity.py
```

You should see that "I enjoy coding" and "Programming is fun" have higher similarity scores!

---

## 📖 Understanding the Code

### Key Components Explained

#### 1. **FastAPI Application**
```python
app = FastAPI(title="FastAPI Hello World", version="0.1.0")
```
Creates a web application that can handle HTTP requests.

#### 2. **Google AI Client**
```python
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
```
Connects to Google's AI services using your API key.

#### 3. **Pydantic Models**
```python
class EmbeddingRequest(BaseModel):
    text: str
```
Defines the structure of data your API expects and returns. This provides automatic validation!

#### 4. **Endpoints (Routes)**
```python
@app.post("/embeddings")
async def generate_embeddings(request: EmbeddingRequest):
```
- `@app.post` means this endpoint accepts POST requests
- `/embeddings` is the URL path
- `async` makes it handle multiple requests efficiently

#### 5. **Embedding Generation**
```python
result = client.models.embed_content(
    model="text-embedding-004",
    contents=request.text,
)
```
Sends text to Google's AI model and gets back a numerical representation (embedding).

#### 6. **PDF Text Extraction**
```python
pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
for page_num in range(pdf_document.page_count):
    page = pdf_document[page_num]
    extracted_text += page.get_text()
```
Reads each page of the PDF and extracts all text.

#### 7. **Cosine Similarity**
```python
similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
```
Calculates how similar two embeddings are (values from 0 to 1, where 1 is most similar).

---

## 🎓 Learning Challenges

Try these exercises to deepen your understanding:

### Challenge 1: Add a New Endpoint
Create a `/greet/{name}` endpoint that returns a personalized greeting.

**Hint:**
```python
@app.get("/greet/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
```

### Challenge 2: Add Error Handling
What happens if someone sends an empty text to `/embeddings`? Add validation!

### Challenge 3: Save Embeddings to a File
Modify the PDF endpoint to save embeddings to a JSON file.

### Challenge 4: Compare Multiple PDFs
Create an endpoint that accepts multiple PDFs and finds the most similar ones.

---

## 🐛 Common Issues and Solutions

### Issue 1: "GOOGLE_API_KEY not found"
**Solution:** Make sure your `.env` file exists and contains your API key.

### Issue 2: "Port 8000 already in use"
**Solution:** Stop any other programs using port 8000, or change the port in `__init__.py`:
```python
uvicorn.run("fastapi_hello.main:app", host="0.0.0.0", port=8001, reload=True)
```

### Issue 3: "Module not found"
**Solution:** Make sure you ran `uv sync` to install all dependencies.

### Issue 4: PDF extraction returns empty text
**Solution:** The PDF might contain only images. Try a different PDF with actual text.

---

## 📚 Key Concepts Summary

| Concept | What It Does |
|---------|--------------|
| **FastAPI** | Web framework for building APIs quickly |
| **Embeddings** | Numerical representations of text that capture meaning |
| **REST API** | A way for programs to communicate over the internet |
| **Endpoints** | URLs that perform specific actions (like `/embeddings`) |
| **Pydantic** | Validates data automatically |
| **Async/Await** | Handles multiple requests efficiently |
| **Environment Variables** | Store secrets like API keys safely |
| **Cosine Similarity** | Measures how similar two embeddings are |

---

## 🚀 Next Steps

Now that you've built this project, you can:

1. **Add a database** to store embeddings (SQLite, PostgreSQL)
2. **Build a search engine** using the similarity endpoint
3. **Create a frontend** with React or HTML/JavaScript
4. **Deploy to the cloud** (Heroku, AWS, Google Cloud)
5. **Add authentication** to protect your API
6. **Build a RAG system** (Retrieval-Augmented Generation) for AI chatbots

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google AI Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [Understanding Embeddings](https://developers.google.com/machine-learning/crash-course/embeddings/video-lecture)
- [REST API Tutorial](https://restfulapi.net/)

---

## 🎉 Congratulations!

You've successfully built a FastAPI application with AI-powered text embeddings! You now understand:
- How to build REST APIs with FastAPI
- How to work with AI models
- How to process PDF files
- How to calculate text similarity

Keep experimenting and building! 🚀
