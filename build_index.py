from config import documents_directory
from ingest import load_all_documents
from chunking import chunk_documents
from vector_store import get_embeddings, build_index, save_index


def main():
    print(f"[build_index] Ingesting from '{documents_directory}'...")
    documents = load_all_documents(documents_directory)

    if not documents:
        print("[build_index] No documents were loaded. Check the folder path / file types.")
        return

    chunks = chunk_documents(documents)
    embeddings = get_embeddings()
    index = build_index(chunks, embeddings)
    save_index(index)
    print("[build_index] Done.")


if __name__ == "__main__":
    main()
