"""Vector store setup for product search."""

from typing import List
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class ProductVectorStore:
    """Manages vector store for product search."""

    def __init__(self):
        """
        Initialize vector store with embeddings.
        """
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        self.vectorstore = None
        self.products_df = None

    def load_products(self, csv_path: str) -> pd.DataFrame:
        """Load products from CSV file."""
        self.products_df = pd.read_csv(csv_path)
        return self.products_df

    def create_documents(self) -> List[Document]:
        """Convert products DataFrame to LangChain Documents."""
        if self.products_df is None:
            raise ValueError("Products must be loaded first")

        documents = []
        for _, row in self.products_df.iterrows():
            # Create rich product description for better search
            content = f"""
            Product: {row['name']}
            Category: {row['category']}
            Brand: {row['brand']}
            Description: {row['description']}
            Price: ${row['price']}
            """

            doc = Document(
                page_content=content.strip(),
                metadata={
                    "id": int(row["id"]),
                    "name": row["name"],
                    "category": row["category"],
                    "brand": row["brand"],
                    "price": float(row["price"]),
                    "description": row["description"],
                },
            )
            documents.append(doc)

        return documents

    def build_vectorstore(self, csv_path: str):
        """Build vector store from products CSV."""
        print("Loading products...")
        self.load_products(csv_path)

        print("Creating documents...")
        documents = self.create_documents()

        print(f"Indexing {len(documents)} products...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        print("Vector store created successfully!")

    def get_retriever(self, k: int = 3):
        """Get retriever with top-k results."""
        if self.vectorstore is None:
            raise ValueError("Vector store must be built first")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def save_vectorstore(self, path: str):
        """Save vector store to disk."""
        if self.vectorstore is None:
            raise ValueError("Vector store must be built first")
        self.vectorstore.save_local(path)
        print(f"Vector store saved to {path}")

    def load_vectorstore(self, path: str):
        """Load vector store from disk."""
        self.vectorstore = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True
        )
        print(f"Vector store loaded from {path}")
