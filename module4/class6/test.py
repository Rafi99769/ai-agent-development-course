from src.tools import search_knowledge_base

result = search_knowledge_base.invoke({"query": "What is the contact email for the company?"})

print(result)