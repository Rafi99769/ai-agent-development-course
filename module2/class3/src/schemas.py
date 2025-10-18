from typing import TypedDict, Annotated
from operator import add
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
