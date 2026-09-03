import json
import re
import csv

import torch
from unsloth import FastLanguageModel

MAX_NEW_TOKENS = 256


def extract_source(text):
    m = re.search(r"\[Source:\s*(.+?)\]", text)
    return m.group(1).strip() if m else None


def keyword_recall(reference, generated):
    ref_tokens = set(re.findall(r"\b\w{4,}\b", reference.lower()))
    gen_tokens = set(re.findall(r"\b\w{4,}\b", generated.lower()))
    if not ref_tokens:
        return 1.0
    return len(ref_tokens & gen_tokens) / len(ref_tokens)


def load_val_set(path="val.jsonl"):
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def generate(model, tokenizer, system_prompt, question):
    FastLanguageModel.for_inference(model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to("cuda")
    outputs = model.generate(
        input_ids=inputs, max_new_tokens=MAX_NEW_TOKENS, temperature=0.3, do_sample=True
    )
    return tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)


def evaluate(model, tokenizer, val_examples, label):
    rows = []
    for ex in val_examples:
        system_prompt = ex["messages"][0]["content"]
        question = ex["messages"][1]["content"]
        reference = ex["messages"][2]["content"]
        expected_source = extract_source(reference)

        generated = generate(model, tokenizer, system_prompt, question)
        got_source = extract_source(generated)

        rows.append({
            "model": label,
            "question": question,
            "expected_source": expected_source,
            "got_source": got_source,
            "citation_ok": int(got_source == expected_source),
            "keyword_recall": round(keyword_recall(reference, generated), 3),
            "length_ratio": round(len(generated) / max(len(reference), 1), 2),
            "generated": generated,
        })
    return rows


def summarize(rows, label):
    n = len(rows)
    citation_rate = sum(r["citation_ok"] for r in rows) / n
    avg_recall = sum(r["keyword_recall"] for r in rows) / n
    avg_len_ratio = sum(r["length_ratio"] for r in rows) / n
    print(f"\n=== {label} ===")
    print(f"  Correct citation rate   : {citation_rate:.1%}")
    print(f"  Avg keyword recall      : {avg_recall:.1%}")
    print(f"  Avg length ratio        : {avg_len_ratio:.2f}")
    return {"citation_rate": citation_rate, "avg_recall": avg_recall, "avg_len_ratio": avg_len_ratio}


if __name__ == "__main__":
    val_examples = load_val_set("val.jsonl")
    print(f"{len(val_examples)} validation questions loaded.")


    base_model, base_tok = FastLanguageModel.from_pretrained(
        model_name="unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
        max_seq_length=2048, load_in_4bit=True,
    )
    base_rows = evaluate(base_model, base_tok, val_examples, "base")
    base_summary = summarize(base_rows, "Qwen2.5-3B-Instruct (base, zero-shot)")
    del base_model
    torch.cuda.empty_cache()


    ft_model, ft_tok = FastLanguageModel.from_pretrained(
        model_name="sfm_qlora_adapter",  # folder saved at step 8a of the notebook
        max_seq_length=2048, load_in_4bit=True,
    )
    ft_rows = evaluate(ft_model, ft_tok, val_examples, "fine-tuned")
    ft_summary = summarize(ft_rows, "Qwen2.5-3B SFM fine-tuned (QLoRA)")


    all_rows = base_rows + ft_rows
    with open("eval_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nDetailed results exported to eval_results.csv")
    print("\n=== COMPARISON TABLE (to insert into the report) ===")
    print(f"{'Metric':<28}{'Base (zero-shot)':<20}{'Fine-tuned (QLoRA)':<20}")
    print(f"{'Correct citation rate':<28}{base_summary['citation_rate']:<20.1%}{ft_summary['citation_rate']:<20.1%}")
    print(f"{'Avg keyword recall':<28}{base_summary['avg_recall']:<20.1%}{ft_summary['avg_recall']:<20.1%}")
