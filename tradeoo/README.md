# Trading Dataset Generator

## Executive Summary

This Trading Dataset Generator is a production-ready system for creating high-quality, LLM-ready instruction-tuning datasets in the trading domain. It generates synthetic examples across four critical categories: PineScript v5 strategies, price-action pattern explanations, institutional flow (FII/DII) analysis, and synthetic OHLC time-series data. The system outputs JSONL files compatible with OpenAI fine-tuning and HuggingFace TRL, plus CSV exports for time-series analysis.

The generator employs template-based synthesis with controlled randomization, ensuring reproducibility through seeding while maintaining diversity through parameter variation. Each generated example includes rich metadata (pattern type, timeframe, confidence, provenance) enabling downstream filtering and quality control. Built-in validation layers check syntactic correctness (PineScript linting), semantic consistency (OHLC pattern matching), and executable verification where applicable.

The architecture supports both CLI batch generation and interactive Streamlit UI, with configurable dataset sizes (1K-100K samples), balanced sampling across categories, and export to multiple formats. The system is designed for ML engineers and quants who need domain-specific training data for LLMs, with clear provenance tracking and ethical safeguards.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate 1000 samples via CLI
python cli.py generate --size 1000 --output datasets/trading_1k.jsonl

# Launch Streamlit UI
streamlit run app.py

# Run validation on existing dataset
python cli.py validate --input datasets/trading_1k.jsonl
```

## Project Structure

```
tradeoo/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.yaml                  # Configuration parameters
├── cli.py                       # Command-line interface
├── app.py                       # Streamlit web UI
├── src/
│   ├── __init__.py
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── pinescript.py       # PineScript strategy generator
│   │   ├── price_action.py     # Price-action explanation generator
│   │   ├── institutional.py    # FII/DII flow generator
│   │   └── ohlc.py             # Synthetic OHLC generator
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── syntax.py           # Syntactic validation
│   │   ├── semantic.py         # Semantic validation
│   │   └── executable.py       # Executable validation
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── jsonl.py            # JSONL export
│   │   └── csv.py              # CSV export
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── randomization.py    # Randomization utilities
│   │   └── metadata.py         # Metadata generation
│   └── schemas.py              # Data schemas
├── templates/
│   ├── pinescript/             # PineScript templates
│   ├── price_action/           # Price-action templates
│   └── institutional/          # Institutional flow templates
├── tests/
│   ├── __init__.py
│   ├── test_generators.py
│   ├── test_validators.py
│   └── test_exporters.py
├── datasets/                   # Generated datasets
├── docs/
│   ├── PLAN.md                 # Detailed implementation plan
│   ├── TEMPLATES.md            # All templates with examples
│   ├── SCHEMA.md               # Data schema documentation
│   ├── VALIDATION.md           # Validation rules
│   ├── FINETUNING.md           # LLM fine-tuning guide
│   └── LEGAL.md                # Legal and ethical considerations
└── Dockerfile                  # Container definition
```

## Features

- **Multi-Domain Generation**: PineScript, price-action, institutional flows, OHLC
- **Template-Based**: 20+ curated templates with controlled randomization
- **Validation Pipeline**: Syntactic, semantic, and executable checks
- **Multiple Formats**: JSONL (LLM-ready), CSV (time-series)
- **Rich Metadata**: Pattern type, timeframe, confidence, provenance
- **Reproducible**: Seed-based generation for deterministic outputs
- **Scalable**: Generate 1K to 100K+ samples
- **Quality Metrics**: Uniqueness, coverage, syntax correctness
- **Dual Interface**: CLI for automation, Streamlit for exploration
- **Production-Ready**: Docker support, CI/CD templates, monitoring

## Dataset Sizes

- **Small**: 1,000 samples (quick testing)
- **Medium**: 10,000 samples (initial fine-tuning)
- **Large**: 100,000 samples (production training)

## Documentation

See `docs/` folder for detailed documentation:
- `PLAN.md` - Complete implementation blueprint
- `TEMPLATES.md` - All templates with examples
- `SCHEMA.md` - JSONL and CSV schemas
- `VALIDATION.md` - Validation rules and checks
- `FINETUNING.md` - How to fine-tune LLMs
- `LEGAL.md` - Legal and ethical guidelines

## License

MIT License - See LICENSE file
