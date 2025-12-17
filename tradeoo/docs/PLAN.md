# Complete Implementation Plan

## A. Executive Summary

The Trading Dataset Generator is a specialized ML pipeline for creating instruction-tuning datasets in the trading domain. It addresses the scarcity of high-quality, domain-specific training data for LLMs by synthesizing realistic examples across PineScript strategies, price-action analysis, and institutional flow interpretation.

The system uses template-based generation with controlled randomization to produce diverse, valid examples. Each sample includes rich metadata enabling quality filtering and provenance tracking. The architecture supports both batch CLI generation and interactive Streamlit exploration, with outputs in JSONL (LLM-ready) and CSV formats.

Built for reproducibility and scale, the generator can produce 1K-100K samples with configurable category balancing. Validation layers ensure syntactic correctness, semantic consistency, and executable verification. The system is production-ready with Docker support, testing infrastructure, and clear fine-tuning integration paths.

## B. Data Types & Templates

### 1. PineScript Strategies (5 Templates)

**Template 1: EMA Crossover**
- Parameters: fast_len (8-21), slow_len (50-200)
- Instruction: "Write a PineScript v5 strategy for EMA crossover with {fast_len} and {slow_len} periods"
- Example Output: See `src/generators/pinescript.py`

**Template 2: RSI + EMA**
- Parameters: rsi_len (10-21), ema_len (20-100), oversold (20-35), overbought (65-80)
- Instruction: "Create a PineScript v5 strategy combining RSI({rsi_len}) and EMA({ema_len})"

**Template 3: Bollinger Breakout**
- Parameters: bb_len (15-25), bb_mult (1.5-2.5)
- Instruction: "Write a PineScript v5 Bollinger Band breakout strategy"

**Template 4: VWAP Scalper**
- Parameters: tp_pct (0.5-3.0), sl_pct (0.3-2.0)
- Instruction: "Create a PineScript v5 VWAP scalping strategy"

**Template 5: Multi-Timeframe**
- Parameters: htf (15/60/240/D), htf_len (20-50), rsi_len (10-21)
- Instruction: "Write a PineScript v5 multi-timeframe strategy"

### 2. Price-Action Explanations (8 Templates)

**Template 1: Retest**
- Explains level flip validation after breakout
- Includes entry, stop, and continuation criteria

**Template 2: Breakout**
- Describes consolidation exit with volume confirmation
- Measured move targets and invalidation rules

**Template 3: False Breakout**
- Identifies fakeout characteristics
- Reversal trading setup

**Template 4: Pin Bar**
- Bullish/bearish rejection candles
- Wick-to-body ratio requirements

**Template 5: Engulfing**
- Two-candle reversal pattern
- Momentum shift signals

**Template 6: HH/HL (Higher Highs/Higher Lows)**
- Uptrend structure identification
- Trendline support trading

**Template 7: LH/LL (Lower Highs/Lower Lows)**
- Downtrend structure
- Resistance trading

**Template 8: Order Block**
- Institutional accumulation/distribution zones
- Retest entry logic

### 3. Institutional Flow (5 Templates)

**Template 1: FII Buying**
- FII bought ₹X Cr, DII sold ₹Y Cr
- Net flow calculation and sentiment

**Template 2: DII Support**
- DII absorption of FII outflows
- Stabilization analysis

**Template 3: Dual Selling**
- Combined institutional outflows
- Bearish pressure assessment

**Template 4: Dual Buying**
- Strong institutional inflows
- Rally potential

**Template 5: Mixed Flow**
- Divergent FII/DII actions
- Sector rotation implications

### 4. Synthetic OHLC Generator

**Algorithm:**
1. Select pattern type (uptrend, downtrend, breakout, pin_bar, engulfing)
2. Initialize base price (100-500 range)
3. Generate 5-20 bars with pattern-specific logic
4. Add realistic noise and volume
5. Ensure OHLC constraints (H≥max(O,C), L≤min(O,C))

**Patterns Supported:**
- Uptrend: Sequential higher closes with 0.2-1.5% gains
- Downtrend: Sequential lower closes with 0.2-1.5% losses
- Breakout: Consolidation (n-3 bars) + volume spike breakout (3 bars)
- Pin Bar: Long wick (2-3x body), small body at opposite end
- Engulfing: Small candle + larger opposite-color candle

**Code:** See `src/generators/ohlc.py`

## C. Labeling & Metadata Schema

### Required Fields

```json
{
  "id": "uuid-v4-string",
  "instruction": "Input question or task",
  "response": "Expected output or answer",
  "pattern_type": "pinescript|price_action|institutional|ohlc",
  "timeframe": "1m|5m|15m|1h|4h|1D|null",
  "ticker": "AAPL|BTCUSD|NIFTY|null",
  "source": "synthetic|real",
  "created_at": "ISO-8601 timestamp",
  "seed": "integer for reproducibility",
  "confidence": "0.0-1.0 quality score",
  "language": "en",
  "metadata": {
    "template": "template_name",
    "params": {...},
    "ohlc_snippet": [...]
  }
}
```

### Example JSONL Object

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "instruction": "Write a PineScript v5 strategy for EMA crossover with 13 and 89 periods",
  "response": "//@version=5\nstrategy(\"EMA Crossover\", overlay=true)...",
  "pattern_type": "pinescript",
  "timeframe": null,
  "ticker": null,
  "source": "synthetic",
  "created_at": "2024-12-03T13:01:57Z",
  "seed": 42,
  "confidence": 1.0,
  "language": "en",
  "metadata": {
    "template": "EMA_Crossover",
    "params": {"fast_len": 13, "slow_len": 89}
  }
}
```

## D. Generation Rules & Randomization

### Parameter Randomization

**Distribution Types:**
- Uniform: Most parameters (EMA lengths, percentages)
- Log-uniform: Large range parameters (volume, price levels)
- Discrete choice: Timeframes, directions, pattern types

**Ranges:**
- EMA lengths: 8-200 (uniform int)
- RSI lengths: 10-21 (uniform int)
- Stop loss %: 0.3-5.0 (uniform float, 2 decimals)
- Take profit %: 0.5-10.0 (uniform float, 2 decimals)
- Bollinger mult: 1.5-3.0 (uniform float, 1 decimal)
- Price levels: 100-500 (uniform float, 2 decimals)
- FII/DII flows: 300-5000 Cr (uniform int)

### Seeding Strategy

- Global seed: Controls overall dataset reproducibility
- Per-sample seed: Enables individual sample regeneration
- Seed = global_seed + sample_index (deterministic)
- Seed = random(0, 1M) (non-deterministic mode)

### Diversity Mechanisms

- Template rotation: Round-robin or weighted random
- Parameter jittering: ±10% variation on regeneration
- Text variation: Synonyms, phrasing alternatives
- Combination: Multi-indicator strategies

## E. Validation Checks

### Syntactic Validation

**PineScript:**
- Contains `//@version=5` declaration
- Balanced parentheses, brackets, braces
- Required functions present: `strategy()`, `input.*()`, `ta.*()`, `plot()`
- No syntax errors (regex-based check)
- Proper indentation (4 spaces)

**Price Action:**
- Instruction is question or command
- Response contains actionable information
- Mentions entry, stop, or target
- Reasonable length (50-500 words)

**Institutional:**
- Contains numeric flow values
- Mentions FII or DII
- Includes sentiment keyword
- Date format valid

### Semantic Validation

**OHLC Consistency:**
- High ≥ max(Open, Close)
- Low ≤ min(Open, Close)
- High ≥ Low
- Volume ≥ 0
- Timestamps sequential

**Pattern Matching:**
- Uptrend: Each close > prior close (80%+ bars)
- Downtrend: Each close < prior close (80%+ bars)
- Pin bar: Wick length > 2× body length
- Engulfing: Second candle range > first candle range

**Parameter Validity:**
- Fast EMA < Slow EMA
- Oversold < Overbought
- Stop loss < Take profit (usually)
- Positive lengths and multipliers

### Executable Validation

**PineScript Linting:**
- Pipe code to external linter (if available)
- Check for common errors: undefined variables, wrong types
- Verify function signatures match PineScript v5 API

**Backtest Simulation:**
- Use vectorbt or similar library
- Run on synthetic OHLC data
- Verify strategy executes without errors
- Check for reasonable metrics (not 100% win rate)

**Code:** See `src/validators/` (to be implemented)

## F. Data Formats & Export

### JSONL Schema

**Format:** One JSON object per line (newline-delimited)

**Structure:**
```jsonl
{"id": "...", "instruction": "...", "response": "...", ...}
{"id": "...", "instruction": "...", "response": "...", ...}
```

**Advantages:**
- Streaming-friendly
- Line-by-line processing
- OpenAI/HuggingFace compatible
- Easy to split/merge

### CSV Format

**For OHLC Data:**
```csv
id,timestamp,open,high,low,close,volume,pattern,ticker
uuid1,2024-01-01T09:00:00,100.00,101.50,99.80,101.20,50000,uptrend,AAPL
```

**For Labels:**
```csv
id,pattern_type,timeframe,confidence,created_at
uuid1,pinescript,null,1.0,2024-12-03T13:01:57Z
```

### File Naming Conventions

```
datasets/
  trading_{size}_{date}.jsonl          # Main dataset
  trading_{size}_{date}_ohlc.csv       # OHLC snippets
  trading_{size}_{date}_labels.csv     # Label file
  trading_{size}_{date}_metadata.json  # Dataset metadata
```

**Example:**
- `trading_10k_20241203.jsonl`
- `trading_10k_20241203_ohlc.csv`

## G. Dataset Sizing & Sampling Strategy

### Size Tiers

| Tier | Samples | Use Case | Generation Time |
|------|---------|----------|-----------------|
| Small | 1,000 | Quick testing, prototyping | ~10 seconds |
| Medium | 10,000 | Initial fine-tuning | ~2 minutes |
| Large | 100,000 | Production training | ~20 minutes |
| XL | 1,000,000 | Large-scale training | ~3 hours |

### Category Balancing

**Balanced (Default):**
- PineScript: 33%
- Price Action: 33%
- Institutional: 33%

**Custom Weights:**
- PineScript: 30%
- Price Action: 40%
- Institutional: 30%

**Rationale:**
- Price action most common in trading
- PineScript requires more tokens (code)
- Institutional flows are niche but valuable

### Sampling Strategy

1. **Stratified Sampling:** Ensure each template represented
2. **Template Rotation:** Cycle through templates evenly
3. **Parameter Diversity:** Wide parameter ranges
4. **Shuffle:** Randomize final order to prevent ordering bias

## H. Tests & Metrics

### Unit Tests

**Generator Tests:**
- Each generator produces valid output
- Seeding produces deterministic results
- Parameter ranges respected
- No crashes on edge cases

**Validator Tests:**
- Syntactic checks catch errors
- Semantic checks validate patterns
- False positives/negatives measured

**Exporter Tests:**
- JSONL format valid
- CSV format valid
- File I/O works correctly

**Code:** See `tests/test_*.py`

### Quality Metrics

**Uniqueness:**
- Measure: Exact duplicate rate (should be <1%)
- Fuzzy duplicate rate using embeddings (should be <5%)
- Instruction diversity (unique instruction count / total)

**Coverage:**
- Template coverage: All templates used
- Parameter coverage: Full range utilized
- Pattern coverage: All patterns represented

**Syntactic Correctness:**
- PineScript: % passing syntax check (target: >95%)
- OHLC: % passing constraint check (target: 100%)
- JSON: % valid JSON objects (target: 100%)

**Semantic Correctness:**
- Pattern matching: % OHLC matching described pattern (target: >90%)
- Parameter validity: % valid parameter combinations (target: 100%)

**Downstream Performance:**
- Model perplexity on held-out test set
- Fine-tuned model accuracy on trading tasks
- Human evaluation scores (1-5 scale)

### Testing Plan

1. **Unit Tests:** Run on every commit (pytest)
2. **Integration Tests:** Full pipeline test (generate → validate → export)
3. **Quality Tests:** Metrics calculation on sample datasets
4. **Regression Tests:** Compare metrics across versions
5. **Human Evaluation:** Sample 100 examples, expert review

## I. Pipeline & Infrastructure

### CLI Commands

```bash
# Generate dataset
python cli.py generate --size 10000 --output datasets/trading_10k.jsonl --seed 42

# Validate dataset
python cli.py validate --input datasets/trading_10k.jsonl

# Show statistics
python cli.py stats --input datasets/trading_10k.jsonl

# Export to CSV
python cli.py export --input datasets/trading_10k.jsonl --format csv
```

### Streamlit UI

**Endpoints:**
- `/` - Main generation interface
- `/preview` - Sample preview
- `/validate` - Upload and validate
- `/stats` - Dataset statistics

**Features:**
- Interactive parameter tuning
- Real-time preview
- Progress tracking
- Download generated files

### Scheduled Generation

**Cron Example:**
```bash
# Daily generation at 2 AM
0 2 * * * cd /path/to/tradeoo && python cli.py generate --size 10000 --output datasets/daily_$(date +\%Y\%m\%d).jsonl
```

**CI/CD Integration:**
```yaml
# GitHub Actions example
name: Generate Dataset
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate
        run: python cli.py generate --size 10000
      - name: Upload
        uses: actions/upload-artifact@v2
        with:
          name: dataset
          path: datasets/
```

### Storage

**Local:**
- `datasets/` directory
- Git LFS for large files

**Cloud:**
- S3: `s3://my-bucket/trading-datasets/`
- GCS: `gs://my-bucket/trading-datasets/`
- Azure Blob: `https://account.blob.core.windows.net/trading-datasets/`

**Versioning:**
- Semantic versioning: `v1.0.0`
- Date-based: `20241203`
- Hash-based: `abc123def`

### Docker Support

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "cli.py", "generate", "--size", "1000"]
```

**Usage:**
```bash
docker build -t trading-dataset-gen .
docker run -v $(pwd)/datasets:/app/datasets trading-dataset-gen
```

## J. Legal & Ethical Considerations

### Copyright

- **Synthetic Data:** No copyright issues (generated, not scraped)
- **Templates:** Original work, MIT licensed
- **Attribution:** Cite this generator if used in research

### Scraping Rules

- **Not Applicable:** This generator creates synthetic data
- **If Adding Real Data:** Respect robots.txt, rate limits, ToS
- **Public Data:** Ensure proper licensing (CC-BY, CC0, etc.)

### Privacy & PII

- **No PII:** Synthetic data contains no personal information
- **Tickers:** Use generic or well-known public tickers only
- **Flows:** Randomized, not real FII/DII data

### Provenance Metadata

**Required Fields:**
- `source`: Always "synthetic" for generated data
- `created_at`: Timestamp of generation
- `seed`: For reproducibility
- `generator_version`: Track generator version

**Recommended:**
- `license`: "MIT" or "CC0"
- `citation`: How to cite
- `contact`: Maintainer email

### Dataset Card

Create `DATASET_CARD.md`:
```markdown
# Trading Dataset v1.0

## Dataset Description
Synthetic instruction-tuning dataset for trading domain LLMs.

## Languages
English

## Dataset Structure
JSONL format with instruction-response pairs.

## Dataset Creation
Generated using template-based synthesis with controlled randomization.

## Considerations
- Synthetic data may not reflect real market conditions
- Use for educational and research purposes
- Not financial advice

## Licensing
MIT License
```

## K. Example Outputs

### Example 1: PineScript

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "instruction": "Write a PineScript v5 strategy for EMA crossover with 13 and 89 periods",
  "response": "//@version=5\nstrategy(\"EMA Crossover\", overlay=true)\nfastLen = input.int(13, \"Fast EMA\")\nslowLen = input.int(89, \"Slow EMA\")\nfastEMA = ta.ema(close, fastLen)\nslowEMA = ta.ema(close, slowLen)\nif ta.crossover(fastEMA, slowEMA)\n    strategy.entry(\"Long\", strategy.long)\nif ta.crossunder(fastEMA, slowEMA)\n    strategy.close(\"Long\")\nplot(fastEMA, color=color.blue)\nplot(slowEMA, color=color.red)",
  "pattern_type": "pinescript",
  "timeframe": null,
  "ticker": null,
  "source": "synthetic",
  "created_at": "2024-12-03T13:01:57Z",
  "seed": 42,
  "confidence": 1.0,
  "language": "en",
  "metadata": {
    "template": "EMA_Crossover",
    "params": {"fast_len": 13, "slow_len": 89}
  }
}
```

### Example 2: Price Action with OHLC

```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "instruction": "Explain the retest pattern at 245.67 level on 1h timeframe",
  "response": "A retest occurs when price breaks through a key level at 245.67, pulls back to test it as new support/resistance, and then continues in the breakout direction. This validates the level flip. On 1h, look for: 1) Initial break with volume, 2) Pullback with lower volume, 3) Bounce/rejection at the level, 4) Continuation move. Entry: on bounce confirmation. Stop: below/above the retested level.",
  "pattern_type": "price_action",
  "timeframe": "1h",
  "ticker": "AAPL",
  "source": "synthetic",
  "created_at": "2024-12-03T13:02:15Z",
  "seed": 123,
  "confidence": 1.0,
  "language": "en",
  "metadata": {
    "template": "Retest",
    "params": {"price": 245.67, "timeframe": "1h"},
    "ohlc_snippet": [
      {"timestamp": "2024-12-03T09:00:00", "open": 243.50, "high": 244.20, "low": 243.10, "close": 244.00, "volume": 25000},
      {"timestamp": "2024-12-03T10:00:00", "open": 244.00, "high": 246.50, "low": 243.80, "close": 246.20, "volume": 45000},
      {"timestamp": "2024-12-03T11:00:00", "open": 246.20, "high": 246.80, "low": 245.50, "close": 245.70, "volume": 30000}
    ]
  }
}
```

### Example 3: FII/DII Flow

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "instruction": "Analyze FII flow: bought ₹2450Cr, DII sold ₹1320Cr on 2024-11-15",
  "response": "FII net buying of ₹2450Cr vs DII selling of ₹1320Cr indicates foreign institutional interest. Net flow: +₹1130Cr. Sentiment: Bullish. Typically supports upside in growth stocks. Sectors: IT, Banking. Watch for continuation if FII buying sustains 3+ days. Reversal risk if DIIs turn buyers or FII flow reverses.",
  "pattern_type": "institutional",
  "timeframe": null,
  "ticker": null,
  "source": "synthetic",
  "created_at": "2024-12-03T13:02:30Z",
  "seed": 456,
  "confidence": 1.0,
  "language": "en",
  "metadata": {
    "template": "FII_Buying",
    "params": {
      "fii_buy": 2450,
      "dii_sell": 1320,
      "net_flow": 1130,
      "date": "2024-11-15",
      "sectors": "IT, Banking",
      "sentiment": "Bullish",
      "market_action": "upside in growth stocks"
    }
  }
}
```

## L. Suggested LLM Settings for Dataset Synthesis

### For GPT-Based Generation (if extending with LLM)

**Temperature:** 0.7-0.9
- Lower (0.7): More consistent, template-like outputs
- Higher (0.9): More creative variations

**Top-p:** 0.9-0.95
- Nucleus sampling for diversity while maintaining quality

**Max Tokens:** 512-1024
- PineScript: 512 tokens
- Price Action: 256 tokens
- Institutional: 256 tokens

**Stop Tokens:** `["\n\n\n", "###", "---"]`
- Prevent run-on generations

**Batch Size:** 10-50
- Balance between throughput and API rate limits

**Frequency Penalty:** 0.3-0.5
- Reduce repetitive phrasing

**Presence Penalty:** 0.2-0.4
- Encourage topic diversity

### For Fine-Tuning

**Learning Rate:** 1e-5 to 5e-5
**Batch Size:** 4-16 (depending on GPU memory)
**Epochs:** 3-5
**Warmup Steps:** 100-500
**Weight Decay:** 0.01
**Gradient Accumulation:** 4-8 steps

## M. How to Fine-Tune an LLM Checklist

### 1. Prepare Dataset

- [ ] Generate dataset using this tool
- [ ] Validate all samples
- [ ] Split into train/val/test (80/10/10)
- [ ] Convert to required format (HuggingFace, OpenAI, etc.)

### 2. Choose Tools

**HuggingFace Transformers + TRL:**
```bash
pip install transformers trl peft accelerate bitsandbytes
```

**AutoTrain:**
```bash
pip install autotrain-advanced
autotrain llm --train --model meta-llama/Llama-2-7b-hf --data-path datasets/
```

**OpenAI Fine-Tuning:**
```bash
openai api fine_tunes.create -t datasets/training.jsonl -m gpt-3.5-turbo
```

### 3. Select Base Model

**Options:**
- Llama 2/3 (7B, 13B, 70B)
- Mistral 7B
- Phi-2/3
- GPT-3.5-turbo (via API)
- Gemma 2B/7B

### 4. Configure QLoRA (Recommended)

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

### 5. Training Script

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-5,
    logging_steps=10,
    save_steps=100,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()
```

### 6. Evaluation

- [ ] Perplexity on test set
- [ ] BLEU/ROUGE scores for responses
- [ ] Human evaluation (sample 100 examples)
- [ ] Task-specific metrics (PineScript syntax correctness, etc.)

### 7. Deployment

- [ ] Export model (HuggingFace Hub, GGUF, etc.)
- [ ] Optimize inference (quantization, vLLM, TensorRT)
- [ ] Create API endpoint
- [ ] Monitor performance

## N. Next Steps for Expanding the Generator

### 1. Real Data Integration

- [ ] Scrape historical price data (yfinance, Alpha Vantage)
- [ ] Integrate real FII/DII flows (NSE, BSE APIs)
- [ ] Add real PineScript examples (TradingView public library)
- [ ] Combine synthetic + real for hybrid datasets

### 2. Reinforcement Learning

- [ ] Implement RLHF (Reinforcement Learning from Human Feedback)
- [ ] Reward model for trading strategy quality
- [ ] PPO training loop
- [ ] Iterative improvement based on backtest results

### 3. Human-in-the-Loop Review

- [ ] Build review interface (Streamlit/Gradio)
- [ ] Collect expert annotations
- [ ] Active learning: prioritize uncertain samples
- [ ] Feedback loop: retrain generators based on corrections

### 4. Model Introspection

- [ ] Attention visualization for PineScript generation
- [ ] Interpretability analysis (LIME, SHAP)
- [ ] Error analysis: categorize failure modes
- [ ] Ablation studies: which templates matter most

### 5. Advanced Features

- [ ] Multi-language support (Hindi, Chinese for Indian/Asian markets)
- [ ] Options strategies (spreads, straddles, etc.)
- [ ] Fundamental analysis (P/E, EPS, etc.)
- [ ] News sentiment integration
- [ ] Multi-modal: charts + text

### 6. Quality Improvements

- [ ] Adversarial validation: train discriminator to detect synthetic data
- [ ] Diversity metrics: measure and optimize
- [ ] Curriculum learning: start simple, increase complexity
- [ ] Ensemble generation: combine multiple generators

### 7. Production Hardening

- [ ] Monitoring and alerting
- [ ] A/B testing framework
- [ ] Versioning and rollback
- [ ] Performance optimization (caching, parallelization)
- [ ] Security audit

### 8. Community & Ecosystem

- [ ] Open-source release
- [ ] Documentation and tutorials
- [ ] Example notebooks
- [ ] Discord/Slack community
- [ ] Contribution guidelines
- [ ] Benchmark leaderboard

---

**End of Implementation Plan**

For detailed code examples, see the `src/` directory and run:
```bash
python cli.py generate --size 100
streamlit run app.py
```
