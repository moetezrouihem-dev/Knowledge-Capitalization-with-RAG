import os
import re
from datetime import datetime

from langchain_core.documents import Document

from config import (
    DOCLING_EXTENSIONS,
    BEAUTIFULSOUP_EXTENSIONS,
    PANDAS_EXTENSIONS,
    WHOLE_DOCUMENT_WORD_THRESHOLD,
    XLSX_WHOLE_SHEET_CHAR_LIMIT,
)

def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _is_whole_document(text):
    return len(text.split()) < WHOLE_DOCUMENT_WORD_THRESHOLD

def _base_metadata(filename, source_type, chunk_whole=False):
    return {
        "source": filename,
        "source_type": source_type,
        "date_ingested": _now_iso(),
        "chunk_whole": chunk_whole,
    }



# Docling: PDF / DOCX

def load_with_docling(file_path):

    from langchain_docling import DoclingLoader
    from langchain_docling.loader import ExportType

    filename = os.path.basename(file_path)
    source_type = filename.rsplit(".", 1)[-1].lower()

    loader = DoclingLoader(file_path=file_path, export_type=ExportType.MARKDOWN)
    raw_docs = loader.load()

    full_text = " ".join(d.page_content for d in raw_docs)
    whole = _is_whole_document(full_text)

    docs = []
    for i, d in enumerate(raw_docs):
        meta = _base_metadata(filename, source_type, chunk_whole=whole)
        docling_page = d.metadata.get("page_no") or d.metadata.get("page")
        meta["page"] = docling_page if docling_page else i + 1
        docs.append(Document(page_content=d.page_content, metadata=meta))
    return docs


# BeautifulSoup: #html

def _extract_js_array(html_text, var_name):
    match = re.search(rf"let\s+{var_name}\s*=\s*\[(.*?)\];", html_text, re.DOTALL)
    return match.group(1) if match else None


def _parse_js_objects(array_text):
    objects = []

    for block in re.findall(r"\{([^{}]*)\}", array_text, re.DOTALL):
        fields = {}
        for key, value in re.findall(r"(\w+)\s*:\s*'((?:[^'\\]|\\.)*)'", block):
            fields[key] = value.replace("\\'", "'")
        if fields:
            objects.append(fields)
    return objects


def load_with_beautifulsoup(file_path):
    from bs4 import BeautifulSoup

    filename = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_text = f.read()

    docs = []

    array_text = _extract_js_array(html_text, "D")
    if array_text:
        entries = _parse_js_objects(array_text)
        for entry in entries:
            content = (
                f"Document: {entry.get('n', '')}\n"
                f"Reference: {entry.get('ref', '')}\n"
                f"Category: {entry.get('cat', '')} / {entry.get('sub', '')}\n"
                f"ISO clause: {entry.get('clause', '')}\n"
                f"Status: {entry.get('st', '')}\n"
                f"Description: {entry.get('desc', '')}"
            )
            meta = _base_metadata(filename, "html", chunk_whole=True)
            meta["page"] = entry.get("id", "?")
            docs.append(Document(page_content=content, metadata=meta))
        print(f"[ingest]   -> extracted {len(entries)} registry entries from JS data")
    else:
        print("[ingest]   -> no 'let D = [...]' array found, falling back to visible text only")

    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    visible_text = soup.get_text(separator="\n", strip=True)
    if visible_text:
        whole = _is_whole_document(visible_text)
        meta = _base_metadata(filename, "html", chunk_whole=whole)
        meta["page"] = "visible_text"
        docs.append(Document(page_content=visible_text, metadata=meta))

    return docs


#Pandas: Excel

def load_with_pandas(file_path):
    import pandas as pd

    filename = os.path.basename(file_path)
    docs = []

    sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

    for sheet_name, df in sheets.items():
        df = df.dropna(how="all")
        if df.empty:
            continue

        row_texts = [
            ", ".join(f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]))
            for _, row in df.iterrows()
        ]
        whole_sheet_text = f"Sheet: {sheet_name}\n" + "\n".join(row_texts)

        if len(whole_sheet_text) < XLSX_WHOLE_SHEET_CHAR_LIMIT:
            meta = _base_metadata(filename, "xlsx", chunk_whole=True)
            meta["page"] = sheet_name
            docs.append(Document(page_content=whole_sheet_text, metadata=meta))
        else:
            for i, row_text in enumerate(row_texts):
                meta = _base_metadata(filename, "xlsx", chunk_whole=True)
                meta["page"] = f"{sheet_name} (row {i + 1})"
                docs.append(
                    Document(
                        page_content=f"Sheet: {sheet_name}\n{row_text}",
                        metadata=meta,
                    )
                )

    return docs

#Router

def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in DOCLING_EXTENSIONS:
            return load_with_docling(file_path)
        elif ext in BEAUTIFULSOUP_EXTENSIONS:
            return load_with_beautifulsoup(file_path)
        elif ext in PANDAS_EXTENSIONS:
            return load_with_pandas(file_path)
        else:
            print(f"[ingest] Skipping unsupported file type: {file_path}")
            return []
    except Exception as e:
        print(f"[ingest] Failed to parse {file_path}: {e}")
        return []


def load_all_documents(folder_path):
    all_docs = []
    for root, _dirs, filenames in os.walk(folder_path):
        for filename in sorted(filenames):
            file_path = os.path.join(root, filename)
            docs = load_file(file_path)
            all_docs.extend(docs)
            print(f"[ingest] {file_path}: {len(docs)} document(s) loaded")

    print(f"[ingest] Total: {len(all_docs)} documents from {folder_path}")
    return all_docs


if __name__ == "__main__":
    from config import documents_directory

    docs = load_all_documents(documents_directory)
    for d in docs[:3]:
        print("---")
        print(d.metadata)
        print(d.page_content[:200])