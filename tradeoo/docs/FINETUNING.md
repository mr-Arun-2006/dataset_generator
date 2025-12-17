# LLM Fine-Tuning Guide

## Overview

This guide shows how to use the generated trading datasets to fine-tune LLMs for trading domain tasks.

## Step 1: Generate Training Data

```bash
# Generate training set (10K samples)
python cli.py generate --size 10000 --output datasets/train.jsonl --seed 42

# Generate validation set (1K samples, different seed)
python cli.py generate --size 1000 --output datasets/val.jsonl --seed 999

# Generate test set (1K samples)
python cli.py generate --size 1000 --output datasets/test.jsonl --seed 777
```

## Step 2: Choose Your Approach

### Option A: HuggingFace Transformers + TRL (Recommended)

**Install:**
```bash
pip install transformers trl peft accelerate bitsandbytes datasets
```

**Fine-tuning Script:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import torch

# Load model
model_name = "meta-llama/Llama-2-7b-hf"  # or mistralai/Mistral-7B-v0.1
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_4bit=True  # QLoRA
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Load dataset
dataset = load_dataset('json', data_files={
    'train': 'datasets/train.jsonl',
    'validation': 'datasets/val.jsonl'
})

# Format function
def format_instruction(example):
    return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./trading-llm",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
    evaluation_strategy="steps",
    save_total_limit=3,
    warmup_steps=100,
    lr_scheduler_type="cosine",
)

# Trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation'],
    peft_config=lora_config,
    formatting_func=format_instruction,
    max_seq_length=512,
)

# Train
trainer.train()

# Save
trainer.save_model("./trading-llm-final")
```

### Option B: OpenAI Fine-Tuning API

**Format Data:**
```python
import jsonlines

# Convert to OpenAI format
with jsonlines.open('datasets/train.jsonl') as reader:
    with jsonlines.open('datasets/train_openai.jsonl', 'w') as writer:
        for obj in reader:
            writer.write({
                "messages": [
                    {"role": "user", "content": obj['instruction']},
                    {"role": "assistant", "content": obj['response']}
                ]
            })
```

**Upload and Fine-tune:**
```bash
# Upload
openai api files.create -f datasets/train_openai.jsonl -p fine-tune

# Fine-tune
openai api fine_tunes.create \
  -t file-abc123 \
  -m gpt-3.5-turbo \
  --n_epochs 3 \
  --learning_rate_multiplier 0.1
```

### Option C: AutoTrain (Easiest)

```bash
pip install autotrain-advanced

autotrain llm \
  --train \
  --model meta-llama/Llama-2-7b-hf \
  --data-path datasets/ \
  --text-column instruction \
  --lr 2e-4 \
  --batch-size 4 \
  --epochs 3 \
  --trainer sft \
  --peft \
  --quantization int4
```

## Step 3: Hyperparameters

### Recommended Settings

**Learning Rate:**
- Base: 2e-4 (with LoRA)
- Full fine-tune: 1e-5 to 5e-5

**Batch Size:**
- 4-8 per device (with gradient accumulation)
- Effective batch size: 16-32

**Epochs:**
- 3-5 epochs (monitor validation loss)

**LoRA Parameters:**
- r: 16 (rank)
- alpha: 32
- dropout: 0.05
- target_modules: q_proj, k_proj, v_proj, o_proj

**Sequence Length:**
- 512 tokens (sufficient for most examples)
- 1024 for longer PineScript strategies

**Warmup:**
- 100-500 steps

**Scheduler:**
- Cosine with warmup (recommended)
- Linear also works

## Step 4: Evaluation

### Perplexity
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("./trading-llm-final")
tokenizer = AutoTokenizer.from_pretrained("./trading-llm-final")
test_data = load_dataset('json', data_files='datasets/test.jsonl')

def compute_perplexity(model, tokenizer, dataset):
    model.eval()
    total_loss = 0
    total_tokens = 0
    
    with torch.no_grad():
        for example in dataset:
            text = f"{example['instruction']}\n{example['response']}"
            inputs = tokenizer(text, return_tensors="pt")
            outputs = model(**inputs, labels=inputs['input_ids'])
            total_loss += outputs.loss.item() * inputs['input_ids'].size(1)
            total_tokens += inputs['input_ids'].size(1)
    
    perplexity = torch.exp(torch.tensor(total_loss / total_tokens))
    return perplexity.item()

ppl = compute_perplexity(model, tokenizer, test_data['train'])
print(f"Test Perplexity: {ppl:.2f}")
```

### Task-Specific Metrics

**PineScript Syntax Correctness:**
```python
import re

def check_pinescript_syntax(code):
    checks = [
        code.startswith('//@version=5'),
        'strategy(' in code or 'indicator(' in code,
        code.count('(') == code.count(')'),
        'ta.' in code or 'strategy.' in code,
    ]
    return sum(checks) / len(checks)

# Test on generated outputs
syntax_scores = [check_pinescript_syntax(output) for output in generated_codes]
print(f"Avg Syntax Score: {sum(syntax_scores)/len(syntax_scores):.2%}")
```

**Human Evaluation:**
```python
# Sample 100 random examples
import random
test_samples = random.sample(test_data['train'], 100)

# Rate on 1-5 scale:
# 1 = Incorrect/Nonsensical
# 2 = Partially correct
# 3 = Correct but generic
# 4 = Correct and specific
# 5 = Excellent, actionable

# Calculate average rating
```

## Step 5: Inference

### Basic Inference
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("./trading-llm-final")
tokenizer = AutoTokenizer.from_pretrained("./trading-llm-final")

def generate_response(instruction):
    prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("### Response:\n")[1]

# Test
instruction = "Write a PineScript v5 strategy for EMA crossover with 12 and 26 periods"
response = generate_response(instruction)
print(response)
```

### Optimized Inference (vLLM)
```bash
pip install vllm

# Serve
vllm serve ./trading-llm-final --port 8000

# Query
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "./trading-llm-final",
    "prompt": "### Instruction:\nExplain pin bar pattern\n\n### Response:\n",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

## Step 6: Deployment

### Option A: HuggingFace Hub
```python
from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="./trading-llm-final",
    repo_id="your-username/trading-llm",
    repo_type="model",
)
```

### Option B: Local API
```python
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Query(BaseModel):
    instruction: str
    max_tokens: int = 256

@app.post("/generate")
def generate(query: Query):
    response = generate_response(query.instruction)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Recommended Models

### Small (< 10GB VRAM)
- Phi-3-mini (3.8B) - Fast, good quality
- Gemma-2B - Efficient
- Mistral-7B-Instruct (4-bit) - Best quality

### Medium (10-24GB VRAM)
- Llama-2-7B / Llama-3-8B
- Mistral-7B (full precision)
- Qwen-7B

### Large (24GB+ VRAM)
- Llama-2-13B
- Mixtral-8x7B
- Llama-3-70B (multi-GPU)

## Tips & Best Practices

1. **Start Small**: Fine-tune on 1K samples first to validate pipeline
2. **Monitor Validation Loss**: Stop if validation loss increases (overfitting)
3. **Use LoRA**: Much faster and cheaper than full fine-tuning
4. **Quantization**: 4-bit (QLoRA) enables larger models on smaller GPUs
5. **Prompt Format**: Keep consistent format (Instruction/Response)
6. **Data Quality**: Better 1K high-quality samples than 10K low-quality
7. **Evaluation**: Always test on held-out data
8. **Versioning**: Track model checkpoints and datasets

## Troubleshooting

**Out of Memory:**
- Reduce batch size
- Enable gradient checkpointing
- Use 4-bit quantization
- Reduce sequence length

**Poor Quality:**
- Increase dataset size
- Lower learning rate
- Train for more epochs
- Check data quality

**Slow Training:**
- Use mixed precision (fp16/bf16)
- Increase batch size with gradient accumulation
- Use faster GPU (A100 > V100 > T4)

## Cost Estimates

**Cloud GPU (RunPod, Lambda Labs):**
- A100 (80GB): $1.99/hr → $6-10 for 10K samples
- A6000 (48GB): $0.79/hr → $3-5 for 10K samples
- RTX 4090 (24GB): $0.44/hr → $2-3 for 10K samples

**OpenAI Fine-Tuning:**
- GPT-3.5-turbo: ~$8 per 1M tokens
- 10K samples ≈ 5M tokens → ~$40

**Recommended**: Start with free Google Colab (T4 GPU) for testing, then scale to paid GPU for production.

---

**Next**: See `docs/PLAN.md` section N for complete fine-tuning checklist.
