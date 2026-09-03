import json
import re
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


HTML_SRC = "SMQ — ISO 9001_2015.html"
html_text = Path("corpus_text/SMQ_ISO_9001_2015.txt").read_text(encoding="utf-8")

entry_re = re.compile(
    r"id: (\S+) \| cat: (\S+) \| sub: (\S+) \| n: (.+?) \| ref: (\S+) \| st: (\S+) \| clause: (\S+) \| link: \S+ \| desc: (.+?)(?=\nid: |\Z)",
    re.DOTALL,
)

entries = []
for m in entry_re.finditer(html_text):
    _id, cat, sub, name, ref, status, clause, desc = m.groups()
    entries.append({
        "id": _id, "cat": cat, "sub": sub, "name": name.strip(),
        "ref": ref, "status": status, "clause": clause, "desc": desc.strip(),
    })

print(f"QMS register entries parsed: {len(entries)}")

for e in entries:
    add(f"What is the document reference for \u00ab {e['name']} \u00bb?",
        f"The reference for this document is {e['ref']}.", HTML_SRC)
    add(f"Which ISO 9001:2015 clause does the document \u00ab {e['name']} \u00bb relate to?",
        f"The document \u00ab {e['name']} \u00bb (ref. {e['ref']}) relates to clause {e['clause']} of the ISO 9001:2015 standard.",
        HTML_SRC)
    add(f"What is the current status of document {e['ref']}?",
        f"Document {e['ref']} ({e['name']}) has the status \u00ab {e['status']} \u00bb.", HTML_SRC)
    if e["desc"]:
        add(f"What does document {e['ref']} ({e['name']}) cover?",
            e["desc"], HTML_SRC)


by_clause = {}
for e in entries:
    by_clause.setdefault(e["clause"], []).append(e["ref"])
for clause, refs in by_clause.items():
    add(f"How many QMS documents are linked to clause {clause} of ISO 9001:2015?",
        f"{len(refs)} document(s) are linked to clause {clause}: {', '.join(refs)}.", HTML_SRC)

by_cat = {}
for e in entries:
    by_cat.setdefault(e["cat"], []).append(e["ref"])
for cat, refs in by_cat.items():
    add(f"How many documents belong to the \u00ab {cat} \u00bb category of the QMS?",
        f"{len(refs)} document(s) belong to the \u00ab {cat} \u00bb category.", HTML_SRC)

add("How many documents in total make up SFM Technologies' ISO 9001:2015 QMS register?",
    f"The QMS register lists {len(entries)} documents in total.", HTML_SRC)


RISK_SRC = "Registre des Risques & Opportunités.xlsx"
risks = [
    dict(ref="R01", desc="ISO 9001 certification not obtained by Q2 2026", p=2, g=5, crit=10, niveau="HIGH", resp="Quality PMO", echeance="March 2026"),
    dict(ref="R02", desc="Deliverables not meeting customer requirements", p=2, g=4, crit=8, niveau="HIGH", resp="Head of Telco Consulting, Engineering & Solutions BU", echeance="Apr. 2026"),
    dict(ref="R03", desc="SaaS solution unavailability (SLA < 99.5%)", p=2, g=5, crit=10, niveau="HIGH", resp="IT Manager", echeance="May 2026"),
    dict(ref="R04", desc="Training satisfaction rate below target (< 90%)", p=2, g=3, crit=6, niveau="MODERATE", resp="Training Director", echeance="June 2026"),
    dict(ref="R05", desc="High senior consultant turnover (> 15%/year)", p=3, g=4, crit=12, niveau="HIGH", resp="HR Manager", echeance="May 2026"),
    dict(ref="R06", desc="Delayed customer collections (rate < 90%)", p=3, g=3, crit=9, niveau="HIGH", resp="Finance Manager", echeance="Apr. 2026"),
    dict(ref="R07", desc="Customer data breach (GDPR incident)", p=1, g=5, crit=5, niveau="MODERATE", resp="IT Manager", echeance="June 2026"),
    dict(ref="R08", desc="RFP conversion rate below target (< 40%)", p=3, g=3, crit=9, niveau="HIGH", resp="Sales Manager", echeance="Apr. 2026"),
    dict(ref="R09", desc="Insufficient internal documentation (unformalized processes)", p=4, g=3, crit=12, niveau="HIGH", resp="PMO + QMS Owner", echeance="2026"),
    dict(ref="R10", desc="Recurring nonconformities on deliverables", p=2, g=4, crit=8, niveau="HIGH", resp="Quality Manager", echeance="Apr. 2026"),
]
opportunities = [
    dict(ref="O01", desc="5G rollout in Africa — surge in regulator RFPs", p=4, g=5, crit=20, niveau="CRITICAL", resp="Head of Telco Consulting, Engineering & Solutions BU", echeance="Q2 2026"),
    dict(ref="O02", desc="ISO 9001 certification = major sales lever for RFPs", p=4, g=5, crit=20, niveau="CRITICAL", resp="Management + PMO", echeance="Q2 2026"),
    dict(ref="O03", desc="Expansion into English-speaking markets (Nigeria, Kenya, Ghana)", p=3, g=4, crit=12, niveau="HIGH", resp="Sales Manager", echeance="Q3 2026"),
    dict(ref="O04", desc="E-learning: scalability across Africa with no logistics costs", p=3, g=4, crit=12, niveau="HIGH", resp="Training Director", echeance="Q3 2026"),
    dict(ref="O05", desc="World Bank / AfDB partnerships — access to major projects", p=4, g=5, crit=20, niveau="CRITICAL", resp="Executive Management", echeance="Ongoing"),
]

for r in risks:
    add(f"What is the criticality of risk {r['ref']} and what is its level?",
        f"Risk {r['ref']} (\u00ab {r['desc']} \u00bb) has a probability of {r['p']}, a severity of {r['g']}, "
        f"giving a criticality of {r['crit']} (P\u00d7G), classified as {r['niveau']} level.", RISK_SRC)
    add(f"Who is responsible for handling risk {r['ref']} and by what deadline?",
        f"The person responsible for handling risk {r['ref']} is {r['resp']}, with a deadline set for {r['echeance']}.", RISK_SRC)

for o in opportunities:
    add(f"What does opportunity {o['ref']} identified in the risks and opportunities register consist of?",
        f"Opportunity {o['ref']} concerns: \u00ab {o['desc']} \u00bb, with a criticality of {o['crit']} (level {o['niveau']}), "
        f"led by {o['resp']} with a target date of {o['echeance']}.", RISK_SRC)

add("How many risks and opportunities are listed in the §6.1 register of SFM Technologies?",
    "The register lists 10 risks and 6 opportunities, for a total of 16 entries.", RISK_SRC)
add("What is the criticality threshold above which a formal action is mandatory according to §6.1.2?",
    "The threshold is set at a criticality (Probability \u00d7 Severity) greater than or equal to 8: above "
    "that, a formal action is mandatory. Between 4 and 7, enhanced monitoring applies; below 4, documented "
    "acceptance is sufficient.", RISK_SRC)


#other Q&A pairs can be added here as needed (private data)

Path("qa_templated.jsonl").write_text(
    "\n".join(json.dumps(ex, ensure_ascii=False) for ex in examples),
    encoding="utf-8",
)
print(f"Total pairs generated (templates): {len(examples)}")
