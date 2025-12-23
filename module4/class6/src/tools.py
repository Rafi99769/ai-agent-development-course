from langchain_core.tools import tool
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

collection_name = "knowledge_base"

@tool
def list_products():
    """
    List all products in the shop including their price, stock, etc.
    """
    product_directory = "data/products.csv"
    
    df = pd.read_csv(product_directory)
    table_md = df.to_markdown()

    return table_md

@tool
def search_knowledge_base(query: str):
    """
    Search the knowledge base for the given query like contact information, FAQ, policies, etc.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=2048)

    q_client = QdrantClient(path="qdrant_store")
    vector_store = QdrantVectorStore(
        client=q_client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    
    results = vector_store.similarity_search(query, k=5)
    
    return "\n".join([r.page_content for r in results])