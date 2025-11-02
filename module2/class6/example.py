"""Example usage of the e-commerce agent."""

from pathlib import Path
from src.agent import build_ecommerce_agent

# Get paths
current_dir = Path(__file__).parent
csv_path = current_dir / "data" / "products.csv"
vector_store_path = current_dir / "data" / "vector_store"

# Build agent
print("Building e-commerce agent...")
agent, product_store = build_ecommerce_agent(
    vector_store_path=str(vector_store_path),
    csv_path=str(csv_path) if csv_path.exists() else None,
)

# Example queries
queries = [
    "I'm looking for wireless headphones",
    "Show me running shoes",
    "What charging cables do you have?",
    "I need a water bottle",
]

print("\n" + "=" * 60)
print("Example Queries")
print("=" * 60)

for query in queries:
    print(f"\nUser: {query}")
    print("Agent:", end=" ")

    # Invoke agent
    response = agent.invoke({"messages": [{"role": "user", "content": query}]})

    # Extract and print response
    if "messages" in response:
        for message in response["messages"]:
            if hasattr(message, "content") and message.content:
                print(message.content)

    print("-" * 60)
