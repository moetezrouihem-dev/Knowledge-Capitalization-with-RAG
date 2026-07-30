import os
Groq_api_key = os.environ.get("GROQ_API_KEY","") 
groq_model = os.environ.get("GROQ_MODEL")

documents_directory = os.environ.get("docs_dir", "docs") 
faiss_index_directory = os.environ.get("faiss_dir", "faiss_index")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # a local embedding model ,small but fast and efficent .

CHUNK_SIZE = 400 # these are only for the pdf and the word documents, the html and excel files will be chunked differently...
CHUNK_OVERLAP = 40

TOP_K = 5  #the answer might be spread across multiple chunks
SCORE_THRESHOLD = None # i'll set this later to filter out low quality answers (but i have to test it before )

DOCLING_EXTENSIONS = {".pdf", ".docx"}
BEAUTIFULSOUP_EXTENSIONS = {".html"}
PANDAS_EXTENSIONS = {".xlsx"}


WHOLE_DOCUMENT_chunking = {
    "Politique Qualité — SFM Technologies.docx",
    "Template Formulaire _ Enregistrement Qualité.docx",
    "Template Procédure SMQ.docx",
    "Template Instruction de Travail SMQ.docx",
    "Plan d_Audit Interne Détaillé — Session AUD-2026-001.docx",
    "Checklist Qualité Avant Remise Livrable — BU Telco (PR1).docx",
    "Organigramme — SFM Technologies.pdf",
    "Cartographie des Processus.pdf",
}

XLSX_WHOLE_SHEET_CHAR_LIMIT = 1500