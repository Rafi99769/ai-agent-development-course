from fastapi import APIRouter
from src.schemas import ChatRequest, ChatResponse
from src.graph import create_graph
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
from langfuse.langchain import CallbackHandler

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/{thread_id}", description="Chat with the AI Assistant", response_model=ChatResponse)
def chat(thread_id: str, request: ChatRequest) -> ChatResponse:
    graph = create_graph()
    callback_handler = CallbackHandler()
    config = {"configurable": {"thread_id": thread_id}, "callbacks": [callback_handler]}

    response = graph.invoke({"messages": [HumanMessage(content=request.query)]}, config=config)
    last_message = response["messages"][-1]
    
    return ChatResponse(ai_assistant=last_message.content)


async def stream_chat_message(thread_id: str, query: str) -> AsyncGenerator[str, None]:
    graph = create_graph()
    callback_handler = CallbackHandler()
    config = {"configurable": {"thread_id": thread_id}, "callbacks": [callback_handler]}

    async for chunk, metadata in graph.astream({"messages": [HumanMessage(content=query)]}, config=config, stream_mode="messages"):
        print(chunk, metadata)
        yield f"data: {chunk.content}\n\n"



@router.post("/ws/{thread_id}", description="Chat with the AI Assistant", response_model=ChatResponse)
async def chat_ws(thread_id: str, request: ChatRequest) -> ChatResponse:
    return StreamingResponse(stream_chat_message(thread_id, request.query), media_type="text/event-stream")

