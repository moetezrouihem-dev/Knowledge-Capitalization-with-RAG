import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import EMBEDDING_MODEL_NAME, faiss_index_directory


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def build_index(chunks, embeddings=None):
    embeddings = embeddings or get_embeddings()
    index = FAISS.from_documents(chunks, embeddings)
    print(f"[vector_store] Built FAISS index with {len(chunks)} chunks")
    return index


def save_index(index, path=faiss_index_directory):
    os.makedirs(path, exist_ok=True)
    index.save_local(path)
    print(f"[vector_store] Saved index to {path}")


def load_index(path=faiss_index_directory, embeddings=None):
    embeddings = embeddings or get_embeddings()
    index = FAISS.load_local(
        path, embeddings, allow_dangerous_deserialization=True
    )
    print(f"[vector_store] Loaded index from {path}")
    return index


def index_exists(path=faiss_index_directory):
    return os.path.exists(os.path.join(path, "index.faiss"))


if __name__ == "__main__":
    from config import documents_directory
    from ingest import load_all_documents
    from chunking import chunk_documents

    docs = load_all_documents(documents_directory)
    chunks = chunk_documents(docs)
    embeddings = get_embeddings()
    index = build_index(chunks, embeddings)
    save_index(index)