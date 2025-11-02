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

        # Use a thread ID for conversation memory
        thread_id = "ecommerce_session_1"
        config = {"configurable": {"thread_id": thread_id}}

        # Interactive loop
        while True:
            query = input("\nYou: ").strip()

            if query.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if not query:
                continue

            print("\nAgent: ", end="", flush=True)

            # Stream response with memory (thread_id in config)
            for step in agent.stream(
                {"messages": [{"role": "user", "content": query}]},
                config=config,
            ):
                for update in step.values():
                    if update is None:
                        continue
                    messages = update.get("messages", []) if isinstance(update, dict) else []
                    for message in messages:
                        # Try using the text property first (simpler)
                        if hasattr(message, "text"):
                            text = message.text
                            if text:
                                print(text, end="", flush=True)
                        # Fallback to content handling
                        elif hasattr(message, "content") and message.content:
                            content = message.content
                            # Handle content blocks (list of dicts)
                            if isinstance(content, list):
                                # Extract text from content blocks
                                for block in content:
                                    if isinstance(block, dict) and block.get("type") == "text":
                                        print(block.get("text", ""), end="", flush=True)
                            elif isinstance(content, str):
                                # Direct string content
                                print(content, end="", flush=True)

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
