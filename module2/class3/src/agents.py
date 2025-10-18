from .prompts import AGENT_SYSTEM_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
from .tools import create_todo, read_todos, update_todo


def get_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
    )

    tools = [create_todo, read_todos, update_todo]
    tool_names = [tool.name for tool in tools]

    prompt = ChatPromptTemplate.from_messages(
        [("system", AGENT_SYSTEM_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )

    prompt = prompt.partial(
        today=datetime.now().strftime("%Y-%m-%d"), tool_names=tool_names
    )

    agent = prompt | llm.bind_tools(tools)

    return agent
