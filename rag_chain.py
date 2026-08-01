from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import re
from config import Groq_api_key, groq_model, TOP_K, SCORE_THRESHOLD

CODE_PATTERN = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+){1,4}\b")

def _extract_codes(text):
    return CODE_PATTERN.findall(text)

SYSTEM_PROMPT = """You are an internal knowledge assistant for a company.
Answer the user's question using ONLY the information in the context below.
Do not use any outside knowledge or invent facts that aren't stated.

Rules:
- Every factual claim you make must end with a citation in the exact
  format [Source: <filename>], taken from the "Source:" line above the
  relevant chunk.
- You MAY combine multiple facts from the context and perform simple
  arithmetic (e.g. multiplying a monthly rate by 12 to get an annual
  figure) as long as every number you use is explicitly stated
  somewhere in the context. Show the calculation briefly.
- Different sections of the same source file are still the same
  source — don't treat "not explicitly in a table" as "not in the
  context" if the fact is stated in prose elsewhere in the same or
  another retrieved chunk.
- Only say the context doesn't have enough information if the numbers
  or facts needed genuinely aren't present anywhere in the context below.
- Be concise and direct.

Context:
{context}
"""


def get_llm(model=groq_model, temperature=0.0):
    if not Groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Export it or put it in a .env file."
        )
    return ChatGroq(model=model, temperature=temperature, api_key=Groq_api_key)


def format_context(chunks):
    blocks = []
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", "?")
        blocks.append(f"Source: {source} (page {page})\n{chunk.page_content}")
    return "\n\n---\n\n".join(blocks)


def _exact_code_matches(question, vectorstore):
    codes = _extract_codes(question)
    if not codes:
        return []
    all_docs = vectorstore.docstore._dict.values()
    return [doc for doc in all_docs if any(code in doc.page_content for code in codes)]


def retrieve(question, vectorstore, k=TOP_K, score_threshold=SCORE_THRESHOLD):
    exact_matches = _exact_code_matches(question, vectorstore)

    if score_threshold is None:
        semantic_results = vectorstore.similarity_search(question, k=k)
    else:
        scored = vectorstore.similarity_search_with_score(question, k=k)
        filtered = [doc for doc, score in scored if score <= score_threshold]
        semantic_results = filtered if filtered else ([scored[0][0]] if scored else [])

    seen_content = {d.page_content for d in exact_matches}
    combined = list(exact_matches)
    for doc in semantic_results:
        if doc.page_content not in seen_content:
            combined.append(doc)
            seen_content.add(doc.page_content)

    return combined


def answer_question(question, vectorstore, llm=None, k=TOP_K, score_threshold=SCORE_THRESHOLD):
    llm = llm or get_llm()
    retrieved_chunks = retrieve(question, vectorstore, k=k, score_threshold=score_threshold)

    if not retrieved_chunks:
        return {
            "answer": "I couldn't find anything relevant in the knowledge base.",
            "sources": [],
        }

    context = format_context(retrieved_chunks)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{question}")]
    )
    chain = prompt | llm

    result = chain.invoke({"context": context, "question": question})

    seen = set()
    sources = []
    for chunk in retrieved_chunks:
        key = (chunk.metadata.get("source"), chunk.metadata.get("page"))
        if key not in seen:
            seen.add(key)
            sources.append({"source": key[0], "page": key[1]})

    return {"answer": result.content, "sources": sources}


if __name__ == "__main__":
    from vector_store import load_index, index_exists

    if not index_exists():
        raise SystemExit("No FAISS index found. Run build_index.py first.")

    vectorstore = load_index()
    question = "What is SFM-PQ-001?"
    result = answer_question(question, vectorstore)
    print(result["answer"])
    print(result["sources"])
