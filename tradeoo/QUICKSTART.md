# Quick Start Guide

## Installation

```bash
# Clone or navigate to the project
cd tradeoo

# Install dependencies
pip install -r requirements.txt
```

## Generate Your First Dataset

### Option 1: CLI (Recommended for automation)

```bash
# Generate 1000 samples
python cli.py generate --size 1000 --output datasets/my_dataset.jsonl

# With reproducible seed
python cli.py generate --size 1000 --output datasets/my_dataset.jsonl --seed 42

# Balanced categories
python cli.py generate --size 1000 --output datasets/my_dataset.jsonl --balance
```

### Option 2: Streamlit UI (Recommended for exploration)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Option 3: Python API

```python
from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional

# Generate single samples
pine_sample = generate_pinescript(seed=42)
price_sample = generate_price_action(seed=123)
inst_sample = generate_institutional(seed=456)

print(pine_sample['instruction'])
print(pine_sample['response'])
```

## Validate Dataset

```bash
python cli.py validate --input datasets/my_dataset.jsonl
```

## View Statistics

```bash
python cli.py stats --input datasets/my_dataset.jsonl
```

## Run Demo

```bash
python demo.py
```

## Next Steps

- Read `docs/PLAN.md` for complete implementation details
- See `docs/EXAMPLES.md` for sample outputs
- Check `docs/FINETUNING.md` for LLM fine-tuning guide
- Explore `src/generators/` to understand templates

## Common Use Cases

### Generate training data for LLM fine-tuning

```bash
python cli.py generate --size 10000 --output datasets/training.jsonl --seed 42
```

### Create test set with different seed

```bash
python cli.py generate --size 1000 --output datasets/test.jsonl --seed 999
```

### Generate large production dataset

```bash
python cli.py generate --size 100000 --output datasets/production.jsonl
```

## Troubleshooting

**Import errors:** Make sure you're in the project root and have installed dependencies

**File not found:** Check that `datasets/` directory exists (created automatically)

**Validation errors:** Check JSONL format (one JSON object per line)

## Support

For issues or questions, see the documentation in `docs/` or create an issue on GitHub.
