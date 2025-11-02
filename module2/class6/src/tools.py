"""Tools for the e-commerce agent."""

from datetime import datetime
from langchain.tools import tool
from langchain_core.retrievers import BaseRetriever


@tool
def create_order(name: str, email: str) -> str:
    """Create an order with user's information and selected products.

    Use this tool when the user wants to confirm their order or checkout.

    Args:
        name: User's full name (will be confirmed/edited by user)
        email: User's email address (will be confirmed/edited by user)

    Returns:
        Confirmation message with order details
    """
    order = {
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_name": name,
        "customer_email": email,
        "order_date": datetime.now().isoformat(),
        "status": "confirmed",
    }

    return (
        f"Order created successfully!\n"
        f"Order ID: {order['order_id']}\n"
        f"Customer: {name}\n"
        f"Email: {email}\n"
        f"Thank you for your order!"
    )


def create_search_products_tool(retriever: BaseRetriever):
    """Create a search_products tool with the given retriever.

    Args:
        retriever: The retriever to use for product search

    Returns:
        A tool instance for searching products
    """
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

    return search_products
