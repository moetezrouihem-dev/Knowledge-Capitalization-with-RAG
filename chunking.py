from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME

_tokenizer = None

def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
    return _tokenizer


def chunk_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    whole_docs = [d for d in documents if d.metadata.get("chunk_whole")]
    to_split = [d for d in documents if not d.metadata.get("chunk_whole")]

    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        _get_tokenizer(),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    split_chunks = splitter.split_documents(to_split) if to_split else []

    chunks = whole_docs + split_chunks
    print(
        f"[chunking] {len(documents)} documents -> "
        f"{len(whole_docs)} kept whole + {len(split_chunks)} split "
        f"= {len(chunks)} chunks"
    )
    return chunks


if __name__ == "__main__":
    from config import documents_directory
    from ingest import load_all_documents

    docs = load_all_documents(documents_directory)
    chunks = chunk_documents(docs)
    print(chunks[0].metadata)
    print(chunks[0].page_content)
