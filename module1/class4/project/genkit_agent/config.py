"""
Configuration management for the Genkit Agent.
"""

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration class for the Genkit Agent."""
    
    google_ai_api_key: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_AI_API_KEY", ""),
        description="Google AI API key for Gemini models"
    )
    
    agent_name: str = Field(
        default_factory=lambda: os.getenv("AGENT_NAME", "Genkit Agent"),
        description="Name of the AI agent"
    )
    
    model_name: str = Field(
        default_factory=lambda: os.getenv("MODEL_NAME", "gemini-1.5-flash"),
        description="Name of the Gemini model to use"
    )
    
    host: str = Field(
        default_factory=lambda: os.getenv("HOST", "localhost"),
        description="Host for the FastAPI server"
    )
    
    port: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000")),
        description="Port for the FastAPI server"
    )
    
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )
    
    def validate_api_key(self) -> bool:
        """
        Validate that the Google AI API key is set.
        
        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.google_ai_api_key and self.google_ai_api_key.strip())


# Global configuration instance
config = Config()