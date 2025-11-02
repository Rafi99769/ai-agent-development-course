"""E-commerce agent using LangChain's create_agent."""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .llms import get_llm, get_small_llm
from .vector_store import ProductVectorStore
from .tools import create_order, create_search_products_tool
from .middlewares import get_all_middlewares
from .prompts import get_system_prompt

load_dotenv()


def build_ecommerce_agent(
    vector_store_path: str = None, csv_path: str = None, top_k: int = 3
):
    """
    Build e-commerce agent with product search capability.

    Args:
        vector_store_path: Path to existing vector store (optional)
        csv_path: Path to products CSV if building new vector store

    Returns:
        Configured agent instance
    """
    # Initialize LLM
    llm = get_llm()
    smol_llm = get_small_llm()

    # Set up vector store
    product_store = ProductVectorStore()

    if vector_store_path and os.path.exists(vector_store_path):
        print(f"Loading existing vector store from {vector_store_path}")
        product_store.load_vectorstore(vector_store_path)
    elif csv_path:
        print(f"Building vector store from {csv_path}")
        product_store.build_vectorstore(csv_path)
        # Save for future use
        if not vector_store_path:
            vector_store_path = "./data/vector_store"
        os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
        product_store.save_vectorstore(vector_store_path)
    else:
        raise ValueError("Either vector_store_path or csv_path must be provided")

    # Get retriever
    retriever = product_store.get_retriever(k=top_k)

    # Create tools
    search_products = create_search_products_tool(retriever)
    tools = [search_products, create_order]

    # Get system prompt
    system_prompt = get_system_prompt(top_k)

    # Get middlewares
    middleware = get_all_middlewares(smol_llm)

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=middleware,
        checkpointer=checkpointer,
    )

    return agent, product_store
