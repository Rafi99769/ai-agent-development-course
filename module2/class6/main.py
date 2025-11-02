"""Main application for e-commerce agent."""

from pathlib import Path
from src.agent import build_ecommerce_agent


def main():
    """Run the e-commerce agent interactively."""
    # Get paths
    current_dir = Path(__file__).parent
    csv_path = current_dir / "data" / "products.csv"
    vector_store_path = current_dir / "data" / "vector_store"

    print("=" * 60)
    print("E-Commerce Product Search Agent")
    print("=" * 60)
    print("\nBuilding agent...")

    # Build agent
    try:
        agent, _ = build_ecommerce_agent(
            vector_store_path=str(vector_store_path),
            csv_path=str(csv_path) if csv_path.exists() else None,
            top_k=3
        )
        print("\nAgent ready! Ask me about products.\n")
        print("Example queries:")
        print("  - 'I'm looking for wireless headphones'")
        print("  - 'Show me running shoes'")
        print("  - 'What charging cables do you have?'")
        print("\nType 'exit' to quit.\n")
        print("-" * 60)

        # Interactive loop
        while True:
            query = input("\nYou: ").strip()

            if query.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if not query:
                continue

            print("\nAgent: ", end="", flush=True)

            # Stream response
            for step in agent.stream(
                {"messages": [{"role": "user", "content": query}]}
            ):
                for update in step.values():
                    messages = update.get("messages", [])
                    for message in messages:
                        if hasattr(message, "content") and message.content:
                            print(message.content, end="", flush=True)

            print("\n")
            print("-" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("  1. Set GOOGLE_AI_API_KEY in your .env file")
        print("  2. Set OPENAI_API_KEY in your .env file")
        print("  3. Installed all dependencies: uv sync")
        raise


if __name__ == "__main__":
    main()
