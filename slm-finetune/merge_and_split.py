import json
import random
from pathlib import Path

random.seed(42)

all_examples = []
for f in ["qa_templated.jsonl", "qa_manual.jsonl", "qa_manual2.jsonl"]:
    for line in Path(f).read_text(encoding="utf-8").splitlines():
        if line.strip():
            all_examples.append(json.loads(line))

print(f"Total before deduplication: {len(all_examples)}")

seen = set()
deduped = []
for ex in all_examples:
    q = ex["messages"][1]["content"]
    if q not in seen:
        seen.add(q)
        deduped.append(ex)

print(f"Total after deduplication: {len(deduped)}")

random.shuffle(deduped)
n_val = max(20, int(len(deduped) * 0.1))
val = deduped[:n_val]
train = deduped[n_val:]

Path("train.jsonl").write_text(
    "\n".join(json.dumps(ex, ensure_ascii=False) for ex in train), encoding="utf-8"
)
Path("val.jsonl").write_text(
    "\n".join(json.dumps(ex, ensure_ascii=False) for ex in val), encoding="utf-8"
)

print(f"train.jsonl : {len(train)} examples")
print(f"val.jsonl   : {len(val)} examples")
