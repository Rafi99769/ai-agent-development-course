"""E-commerce agent using LangChain's create_agent."""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from .llms import get_llm, get_small_llm
from .vector_store import ProductVectorStore

load_dotenv()


def build_ecommerce_agent(vector_store_path: str = None, csv_path: str = None, top_k: int = 3):
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

    # Create custom search tool using @tool decorator
    @tool
    def search_products(query: str) -> str:
        """Search for products in the e-commerce catalog.

        Use this tool to find products that match user queries.
        The tool returns the most relevant products based on name,
        category, brand, description, and price.

        Args:
            query: Natural language query about products
                   (e.g., "wireless headphones", "running shoes")

        Returns:
            Formatted string with top product matches including name, price, and description
        """
        docs = retriever.invoke(query)

        if not docs:
            return "No products found matching your query."

        results = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            result = (
                f"{i}. {metadata.get('name', 'Unknown Product')}\n"
                f"   Price: ${metadata.get('price', 0):.2f}\n"
                f"   Category: {metadata.get('category', 'N/A')}\n"
                f"   Brand: {metadata.get('brand', 'N/A')}\n"
                f"   Description: {metadata.get('description', 'N/A')}\n"
            )
            results.append(result)

        return "\n".join(results)

    # Create agent with system prompt
    system_prompt = (
        "You are a helpful e-commerce assistant that helps users find products. "
        "When a user asks about products, use the search_products tool to find "
        f"the top {top_k} most relevant matches. "
        "Present the results clearly with product names, prices, and key features. "
        "Be friendly, informative, and helpful in your responses."
    )

    summarization_middleware = SummarizationMiddleware(
        model=smol_llm,
        max_tokens_before_summary=2000,
        messages_to_keep=5,
    )

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=llm,
        tools=[search_products],
        system_prompt=system_prompt,
        middleware=[summarization_middleware],
        checkpointer=checkpointer,
    )

    return agent, product_store
