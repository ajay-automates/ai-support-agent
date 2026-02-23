"""
Document Ingestion Pipeline
Handles uploading, chunking, embedding, and storing documents in ChromaDB.
"""

import os
import hashlib
from typing import List
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ============================================================
# CONFIGURATION
# ============================================================
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "vectorstore", "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, free, good quality
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def get_embeddings():
    """Get the embedding model (runs locally, no API cost)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def get_vectorstore(collection_name: str = "default"):
    """Get or create a ChromaDB vectorstore for a specific business."""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )


def chunk_text(text: str, source: str = "uploaded") -> List:
    """Split text into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    docs = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": source}],
    )
    return docs


def ingest_text(text: str, source: str = "pasted_text", collection_name: str = "default") -> int:
    """Ingest raw text into the vectorstore."""
    docs = chunk_text(text, source=source)
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(docs)
    return len(docs)


def ingest_file(file_path: str, collection_name: str = "default") -> int:
    """Ingest a file (PDF, TXT) into the vectorstore."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF, TXT, or MD.")

    raw_docs = loader.load()

    # Chunk the documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    docs = splitter.split_documents(raw_docs)

    # Add to vectorstore
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(docs)

    return len(docs)


def clear_collection(collection_name: str = "default"):
    """Clear all documents from a collection."""
    vectorstore = get_vectorstore(collection_name)
    vectorstore.delete_collection()


def get_collection_stats(collection_name: str = "default") -> dict:
    """Get stats about a collection."""
    vectorstore = get_vectorstore(collection_name)
    collection = vectorstore._collection
    return {
        "collection_name": collection_name,
        "document_count": collection.count(),
    }
