"""
FAISS vector store and embedding utilities for chatbot context retrieval.
"""

from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.settings import settings
import os

# Path to persist the FAISS index (can be changed as needed)
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_post_index")

# Use Gemini embeddings via LangChain
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=settings.GENAI_API_KEY
)


def build_faiss_index(texts: List[str], metadatas: List[dict] = None):
    """
    Build a FAISS index from a list of texts and optional metadata.
    """
    vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
    vectorstore.save_local(FAISS_INDEX_PATH)
    return vectorstore


def load_faiss_index():
    """
    Load the FAISS index from disk, or return None if not found.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        return None
    try:
        return FAISS.load_local(FAISS_INDEX_PATH, embedding_model)
    except Exception:
        return None


def update_faiss_index(new_text: str, metadata: dict = None):
    """
    Add a new text (post) to the FAISS index and persist it.
    """
    vectorstore = load_faiss_index()
    if vectorstore is None:
        vectorstore = FAISS.from_texts(
            [new_text], embedding_model, metadatas=[metadata] if metadata else None
        )
    else:
        vectorstore.add_texts([new_text], metadatas=[metadata] if metadata else None)
    vectorstore.save_local(FAISS_INDEX_PATH)
    return vectorstore


def search_faiss_index(query: str, k: int = 5) -> List[Tuple[str, dict]]:
    """
    Search the FAISS index for the top-k most relevant texts to the query.
    Returns a list of (text, metadata) tuples.
    """
    vectorstore = load_faiss_index()
    if vectorstore is None:
        return []
    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
    return [(doc.page_content, doc.metadata) for doc, _ in docs_and_scores]
