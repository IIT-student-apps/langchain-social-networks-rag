import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os
from src.core.llm_factory import get_embeddings


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedding_function = get_embeddings()

# Use data/chroma_db directory for vector store
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "data/chroma_db")
vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_function)

def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id
            split.metadata['filename'] = os.path.basename(file_path)

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    
def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False


def list_indexed_files():
    try:
        docs = vectorstore.get()
        metadata_list = docs.get("metadatas", [])

        file_info = {}
        for meta in metadata_list:
            fid = meta.get("file_id", "unknown")
            fname = meta.get("filename", "неизвестный_файл")
            key = (fid, fname)
            file_info[key] = file_info.get(key, 0) + 1

        return file_info  # → dict из (fid, filename): кол-во_чанков
    except Exception as e:
        print(f"Error listing files: {e}")
        return {}
