"""Flask API backend for Trading Dataset Generator."""
from datetime import datetime
import json
import random
import uuid
from pathlib import Path

import jsonlines
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.generators.institutional import generate_institutional
from src.generators.ohlc import generate_ohlc_snippet
from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.schemas import TrainingExample

app = Flask(__name__)
CORS(app)

DATASETS_DIR = Path("datasets")
MAX_DATASET_SIZE = 10_000
DATASETS_DIR.mkdir(exist_ok=True)


def _safe_dataset_filename(filename: str) -> str:
    """Return a safe JSONL filename or raise ValueError."""
    safe_name = secure_filename(filename or "")
    if not safe_name or safe_name != filename or not safe_name.lower().endswith(".jsonl"):
        raise ValueError("filename must be a simple .jsonl filename")
    return safe_name


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/preview/<category>", methods=["GET"])
def preview_sample(category):
    """Generate a preview sample for a specific category."""
    try:
        seed = request.args.get("seed", type=int, default=None)
        generators = {
            "pinescript": generate_pinescript,
            "price_action": generate_price_action,
            "institutional": generate_institutional,
        }
        if category not in generators:
            return jsonify({"error": f"Invalid category: {category}"}), 400
        return jsonify(generators[category](seed=seed))
    except Exception:
        app.logger.exception("Preview generation failed")
        return jsonify({"error": "Unable to generate preview"}), 500


@app.route("/api/preview/ohlc", methods=["GET"])
def preview_ohlc():
    """Generate OHLC preview."""
    try:
        pattern = request.args.get("pattern", "breakout")
        num_bars = request.args.get("num_bars", type=int, default=10)
        seed = request.args.get("seed", type=int, default=None)
        if not 1 <= num_bars <= 1_000:
            return jsonify({"error": "num_bars must be between 1 and 1000"}), 400
        return jsonify({"pattern": pattern, "bars": generate_ohlc_snippet(pattern, num_bars=num_bars, seed=seed)})
    except Exception:
        app.logger.exception("OHLC preview generation failed")
        return jsonify({"error": "Unable to generate OHLC preview"}), 500


@app.route("/api/generate", methods=["POST"])
def generate_dataset():
    """Generate and persist a complete dataset."""
    try:
        config = request.get_json(silent=True) or {}
        dataset_size = config.get("size", 100)
        if not isinstance(dataset_size, int) or not 1 <= dataset_size <= MAX_DATASET_SIZE:
            return jsonify({"error": f"size must be an integer between 1 and {MAX_DATASET_SIZE}"}), 400

        seed_value = config.get("seed", 0)
        balance_categories = config.get("balance", True)
        requested_name = config.get(
            "filename", f'trading_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
        )
        try:
            output_name = _safe_dataset_filename(requested_name)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        if balance_categories:
            weights = {"pinescript": 1, "price_action": 1, "institutional": 1}
        else:
            weights = {
                "pinescript": float(config.get("pine_weight", 30)),
                "price_action": float(config.get("price_weight", 40)),
                "institutional": float(config.get("inst_weight", 30)),
            }
            if any(weight < 0 for weight in weights.values()) or sum(weights.values()) <= 0:
                return jsonify({"error": "category weights must be non-negative and have a positive total"}), 400

        actual_seed = seed_value if isinstance(seed_value, int) and seed_value > 0 else random.randint(1, 999999)
        random.seed(actual_seed)

        total_weight = sum(weights.values())
        raw_counts = {name: dataset_size * weight / total_weight for name, weight in weights.items()}
        distribution = {name: int(value) for name, value in raw_counts.items()}
        remainder = dataset_size - sum(distribution.values())
        for name in sorted(raw_counts, key=raw_counts.get, reverse=True)[:remainder]:
            distribution[name] += 1

        generators = {
            "pinescript": generate_pinescript,
            "price_action": generate_price_action,
            "institutional": generate_institutional,
        }
        samples = []
        for category, count in distribution.items():
            for _ in range(count):
                sample_seed = random.randint(0, 1_000_000)
                data = generators[category](seed=sample_seed)
                example = TrainingExample(
                    id=str(uuid.uuid4()),
                    instruction=data["instruction"],
                    response=data["response"],
                    pattern_type=data["pattern_type"],
                    timeframe=data.get("timeframe"),
                    seed=sample_seed,
                    metadata=data.get("metadata", {}),
                )
                samples.append(example.model_dump())

        random.shuffle(samples)
        output_path = DATASETS_DIR / output_name
        with jsonlines.open(output_path, mode="w") as writer:
            writer.write_all(samples)

        return jsonify({
            "success": True,
            "samples_generated": len(samples),
            "filename": output_name,
            "path": str(output_path),
            "seed_used": actual_seed,
            "distribution": distribution,
        })
    except Exception:
        app.logger.exception("Dataset generation failed")
        return jsonify({"error": "Unable to generate dataset"}), 500


@app.route("/api/datasets", methods=["GET"])
def list_datasets():
    """List all generated datasets."""
    try:
        datasets = []
        for file_path in DATASETS_DIR.glob("*.jsonl"):
            stat = file_path.stat()
            with file_path.open("r", encoding="utf-8") as handle:
                line_count = sum(1 for _ in handle)
            datasets.append({
                "name": file_path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "samples": line_count,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return jsonify({"datasets": sorted(datasets, key=lambda item: item["modified"], reverse=True)})
    except Exception:
        app.logger.exception("Dataset listing failed")
        return jsonify({"error": "Unable to list datasets"}), 500


@app.route("/api/datasets/<filename>", methods=["GET"])
def download_dataset(filename):
    """Download a generated JSONL dataset safely."""
    try:
        safe_name = _safe_dataset_filename(filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    file_path = DATASETS_DIR / safe_name
    if not file_path.is_file():
        return jsonify({"error": "Dataset not found"}), 404
    return send_file(file_path, as_attachment=True)


@app.route("/api/validate", methods=["POST"])
def validate_dataset():
    """Validate a JSONL dataset against the TrainingExample schema."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    try:
        file = request.files["file"]
        errors = []
        valid_count = 0
        for line_number, line in enumerate(file.stream, start=1):
            try:
                obj = json.loads(line)
                TrainingExample(**obj)
                valid_count += 1
            except Exception as exc:
                errors.append({"line": line_number, "error": str(exc)})

        return jsonify({
            "valid": len(errors) == 0,
            "valid_count": valid_count,
            "error_count": len(errors),
            "errors": errors[:50],
        })
    except Exception:
        app.logger.exception("Dataset validation failed")
        return jsonify({"error": "Unable to validate dataset"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
