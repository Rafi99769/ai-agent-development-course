from langchain_core.messages import BaseMessage
from typing import Annotated, TypedDict
from operator import add
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add] = []

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=256)

class ChatResponse(BaseModel):
    ai_assistant: str = Field(..., min_length=1)