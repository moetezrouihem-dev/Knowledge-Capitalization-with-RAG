import json
from pathlib import Path

SYSTEM_PROMPT = (
    "You are SFM Technologies' knowledge capitalization assistant. "
    "Answer only from the provided ISO 9001:2015 QMS documents. "
    "Always cite your source in the format [Source: file_name]."
)

examples = []


def add(question, answer, source_file):
    examples.append({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"{answer} [Source: {source_file}]"},
        ]
    })

# i'll provide a single example of a question and answer pair ....others are hidden to assure security and privacy of the data. 

SRC = "Politique Qualité — SFM Technologies.docx"
add("What are the strategic pillars of SFM Technologies' quality policy?",
    "SFM Technologies' quality policy is built around 7 strategic pillars: customer satisfaction and "
    "loyalty, continuous improvement and process control, innovation and technological excellence, "
    "employee skills development, strengthening durable relationships with partners and suppliers, "
    "compliance with regulatory and ethical requirements, and performance and measurable indicator-driven "
    "management.", SRC)

Path("qa_manual.jsonl").write_text(
    "\n".join(json.dumps(ex, ensure_ascii=False) for ex in examples),
    encoding="utf-8",
)
print(f"Total manual pairs generated: {len(examples)}")
