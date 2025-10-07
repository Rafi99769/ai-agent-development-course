"""
Main entry point for the Genkit Agent FastAPI application.
"""

import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from genkit_agent import GenkitAgent, Config

# Load environment variables
load_dotenv()


# Request/Response models for API
class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


class AgentInfoResponse(BaseModel):
    name: str
    model: str
    conversation_length: int
    version: str


# Initialize FastAPI app
app = FastAPI(
    title="Genkit Agent API",
    description="AI Agent built with Google Genkit and Gemini integration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Global agent instance
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        config = Config()
        agent = GenkitAgent(config)
        print(f"✅ Genkit Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint that serves the frontend."""
    frontend_file = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Genkit Agent API is running! Frontend not found.", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Genkit Agent API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the agent."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        response = await agent.generate_response(
            prompt=request.message
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/agent/info", response_model=AgentInfoResponse)
async def get_agent_info():
    """Get agent information."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    info = agent.get_agent_info()
    return AgentInfoResponse(**info)


@app.get("/agent/history")
async def get_conversation_history():
    """Get conversation history."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    return {"history": agent.get_conversation_history()}


@app.post("/agent/clear-history")
async def clear_conversation_history():
    """Clear conversation history."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    agent.clear_history()
    return {"message": "Conversation history cleared"}


def run_server():
    """Run the FastAPI server."""
    config = Config()
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )


if __name__ == "__main__":
    run_server()
