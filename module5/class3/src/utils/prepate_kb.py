from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

DATA_DIR = Path("data")

def prepare_kb():
    """
    Prepare the knowledge base for the agent.
    """
    file_paths = DATA_DIR.glob("*.md")
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
    all_chunks = []
    
    for file_path in file_paths:
        if file_path.suffix != ".pdf":
            content = file_path.read_text()
            chunks = splitter.split_text(content)
            all_chunks.extend([Document(page_content=c) for c in chunks])
        else:
            pdf_loader = PyMuPDFLoader(file_path)
            docs = pdf_loader.load()
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)

    return all_chunks