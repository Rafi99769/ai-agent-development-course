from src.utils.prepate_kb import prepare_kb
from src.vector_store import add_documents

chunks = prepare_kb()
add_documents(chunks)