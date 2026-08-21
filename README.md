# Trading Dataset Generator

A Python-based dataset generation and validation platform for creating structured trading datasets for AI/ML experimentation.

## Engineering Highlights

- **Python + Flask REST API** for health checks, previews, dataset generation, listing, downloads, and validation.
- **Pydantic schema validation** for generated training examples.
- **Deterministic generation** through configurable random seeds for reproducible experiments.
- **Automated dataset validation** for JSONL files with row-level error reporting.
- **Input validation and safe file handling** for dataset generation and downloads.
- **Automated regression tests** using pytest and Flask's test client.
- **GitHub Actions CI** runs the Python test suite on pushes and pull requests.
- Interactive frontend and CLI tooling are included under `tradeoo/`.

## Architecture

```text
Client / Frontend
       |
       v
   Flask REST API
       |
       +--> Generator modules
       |      +--> PineScript
       |      +--> Price Action
       |      +--> Institutional
       |
       +--> Pydantic validation
       |
       +--> JSONL dataset storage
       |
       +--> Dataset validation API
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Service health check |
| `/api/preview/<category>` | GET | Generate a preview sample |
| `/api/preview/ohlc` | GET | Generate OHLC preview data |
| `/api/generate` | POST | Generate a complete JSONL dataset |
| `/api/datasets` | GET | List generated datasets |
| `/api/datasets/<filename>` | GET | Download a dataset |
| `/api/validate` | POST | Validate an uploaded JSONL dataset |

## Run Locally

```bash
cd tradeoo
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python api.py
```

The API runs on `http://localhost:5000`.

## Run Tests

```bash
cd tradeoo
python -m pytest -q
```

The same test suite runs automatically through GitHub Actions for pushes and pull requests.

## Resume Evidence

This project demonstrates practical software engineering skills including Python development, REST API design, input validation, schema validation, automated testing, CI, debugging, reproducible data generation, Git/GitHub workflows, and secure file handling.
