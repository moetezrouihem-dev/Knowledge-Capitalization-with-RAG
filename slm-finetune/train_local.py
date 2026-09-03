import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

import torch
from unsloth import FastLanguageModel
import unsloth.models._utils as _uutils
_uutils.get_statistics = lambda *a, **kw: None
import unsloth.models.llama as _ullama
_ullama.get_statistics = lambda *a, **kw: None

from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

max_seq_length = 1024  # reduced vs 2048 to save VRAM on 6GB

print("Loading base model in 4-bit...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",  # essential on 6GB
    random_state=42,
)

print("Loading dataset...")
dataset = load_dataset("json", data_files={"train": "train.jsonl", "validation": "val.jsonl"})


def formatting_func(example):
    text = tokenizer.apply_chat_template(
        example["messages"], tokenize=False, add_generation_prompt=False
    )
    return {"text": text}


dataset = dataset.map(formatting_func)
print("Formatted example:\n", dataset["train"][0]["text"][:500])

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    args=SFTConfig(
        per_device_train_batch_size=1,       # reduced vs 2 ... VRAM safety margin
        gradient_accumulation_steps=8,       # compensates for the small batch size
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=15,
        save_strategy="no",
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=42,
        output_dir="outputs",
        report_to="none",
    ),
)

print("Starting training...")
trainer.train()

print("Saving LoRA adapter...")
model.save_pretrained("sfm_qlora_adapter")
tokenizer.save_pretrained("sfm_qlora_adapter")

print("Merging and exporting full model (16-bit)...")
model.save_pretrained_merged("sfm_qwen2.5-3b_merged", tokenizer, save_method="merged_16bit")

print("Exporting GGUF for Ollama...")
model.save_pretrained_gguf("sfm_qwen2.5-3b_gguf", tokenizer, quantization_method="q4_k_m")

print("\nDone. Adapter -> sfm_qlora_adapter/  |  GGUF -> sfm_qwen2.5-3b_gguf/")
