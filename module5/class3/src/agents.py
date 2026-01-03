from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT
from .tools import list_products, search_knowledge_base

load_dotenv()

tools = [list_products, search_knowledge_base]

def get_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])

    agent = prompt | llm.bind_tools(tools)

    return agent