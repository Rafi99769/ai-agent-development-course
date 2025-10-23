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
    return {"message": "Hello From RAG!"}


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
            model="gemini-embedding-001",
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
