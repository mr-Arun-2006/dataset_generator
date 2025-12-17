# Sample Outputs

This document contains example outputs from the Trading Dataset Generator.

## Example 1: PineScript Strategy

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

## Example 2: Price Action Analysis

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
    "params": {"price": 245.67, "timeframe": "1h"}
  }
}
```

## Example 3: Institutional Flow Analysis

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

## Running the Generator

Generate your own samples:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate 10 samples
python cli.py generate --size 10 --output datasets/sample.jsonl

# View samples
cat datasets/sample.jsonl | python -m json.tool
```

Or use the Streamlit UI:

```bash
streamlit run app.py
```
