from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(path="qdrant_store")
collection_name = "knowledge_base"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=2048, distance=Distance.COSINE),
    )
client.close()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=2048)


def add_documents(documents):
    """
    Add documents to the vector store.
    """
    q_client = QdrantClient(path="qdrant_store")
    vector_store = QdrantVectorStore(
        client=q_client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    vector_store.add_documents(documents)
