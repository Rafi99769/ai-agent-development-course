"""
Genkit Agent implementation using Google Genkit Python SDK.
"""

import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from genkit import ai
from genkit.plugins import google_genai
from .config import Config


class ChatMessage(BaseModel):
    """Represents a chat message."""
    role: str
    content: str
    timestamp: Optional[str] = None


class GenkitAgent:
    """
    AI Agent using Google Genkit Python SDK for conversational AI.
    """

    def __init__(self, config: Config):
        """
        Initialize the Genkit Agent.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self.conversation_history: List[ChatMessage] = []
        
        # Initialize Genkit with Google AI plugin
        self.ai = ai.Genkit(
            plugins=[google_genai.GoogleAI()],
        )

    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 1000,
        include_history: bool = True
    ) -> str:
        """
        Generate a response using the Genkit AI model.
        
        Args:
            prompt: The user's input prompt
            temperature: Controls randomness in generation (0.0 to 1.0)
            max_output_tokens: Maximum number of tokens to generate
            include_history: Whether to include conversation history in the prompt
            
        Returns:
            Generated response text
        """
        try:
            # Build the full prompt with history if requested
            full_prompt = self._build_prompt_with_history(prompt) if include_history else prompt
            
            # Generate response using Genkit
            response = await self.ai.generate(
                model=f'googleai/{self.config.model_name}',
                prompt=full_prompt,
                config={
                    'temperature': temperature,
                    'maxOutputTokens': max_output_tokens,
                }
            )
            
            response_text = response.text if response.text else "I apologize, but I couldn't generate a response."
            
            # Add to conversation history
            self.add_to_history("user", prompt)
            self.add_to_history("assistant", response_text)
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg

    def _build_prompt_with_history(self, current_prompt: str) -> str:
        """
        Build a prompt that includes conversation history.
        
        Args:
            current_prompt: The current user prompt
            
        Returns:
            Full prompt with history context
        """
        if not self.conversation_history:
            return current_prompt
        
        history_text = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in self.conversation_history[-10:]  # Last 10 messages
        ])
        
        return f"Previous conversation:\n{history_text}\n\nCurrent message:\nuser: {current_prompt}"

    def add_to_history(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user/assistant)
            content: The message content
        """
        message = ChatMessage(role=role, content=content)
        self.conversation_history.append(message)
        
        # Keep only the last 50 messages to prevent memory issues
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history as a list of dictionaries.
        
        Returns:
            List of conversation messages
        """
        return [msg.model_dump() for msg in self.conversation_history]

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent configuration.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "agent_name": self.config.agent_name,
            "model_name": self.config.model_name,
            "conversation_length": len(self.conversation_history),
            "max_history_length": 50
        }