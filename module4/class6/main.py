from src.graph import create_graph
from langchain_core.messages import HumanMessage

graph = create_graph()

config = {"configurable": {"thread_id": "1233"}}

while user_input := input("You: "):
    if user_input.lower() in ["exit", "quit", "q"]:
        break

    response = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    
    last_message = response["messages"][-1]
    print(f"Ast: {last_message.content}")