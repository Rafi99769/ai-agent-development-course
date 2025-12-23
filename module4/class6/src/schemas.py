from langchain_core.messages import BaseMessage
from typing import Annotated, TypedDict
from operator import add

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add] = []
