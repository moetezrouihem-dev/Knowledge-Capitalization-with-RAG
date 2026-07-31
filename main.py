from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from vector_store import get_embeddings, load_index, index_exists
from rag_chain import get_llm, answer_question
from build_index import main as build_index_from_scratch
from config import TOP_K

state = {"vectorstore": None, "llm": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not index_exists():
        print("[main] No FAISS index found on disk, building it now...")
        build_index_from_scratch()

    embeddings = get_embeddings()
    state["vectorstore"] = load_index(embeddings=embeddings)
    state["llm"] = get_llm()
    yield
    state.clear()


app = FastAPI(title="RAG Knowledge Capitalization Service", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    k: int = TOP_K


class SourceItem(BaseModel):
    source: str
    page: int | str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


@app.get("/health")
def health():
    return {"status": "ok", "index_loaded": state["vectorstore"] is not None}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    if state["vectorstore"] is None:
        raise HTTPException(status_code=503, detail="Index not loaded yet.")

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty.")

    result = answer_question(
        question=payload.question,
        vectorstore=state["vectorstore"],
        llm=state["llm"],
        k=payload.k,
    )
    return result


@app.post("/reindex")
def reindex():
    build_index_from_scratch()
    state["vectorstore"] = load_index(embeddings=get_embeddings())
    return {"status": "reindexed"}
