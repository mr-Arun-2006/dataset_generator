"""Flask API backend for Trading Dataset Generator."""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jsonlines
import uuid
import random
from pathlib import Path
from datetime import datetime

from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional
from src.generators.ohlc import generate_ohlc_snippet
from src.schemas import TrainingExample

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Ensure datasets directory exists
Path("datasets").mkdir(exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/preview/<category>', methods=['GET'])
def preview_sample(category):
    """Generate a preview sample for a specific category."""
    try:
        seed = request.args.get('seed', type=int, default=None)
        
        generators = {
            'pinescript': generate_pinescript,
            'price_action': generate_price_action,
            'institutional': generate_institutional
        }
        
        if category not in generators:
            return jsonify({'error': f'Invalid category: {category}'}), 400
        
        data = generators[category](seed=seed)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/ohlc', methods=['GET'])
def preview_ohlc():
    """Generate OHLC preview."""
    try:
        pattern = request.args.get('pattern', 'breakout')
        num_bars = request.args.get('num_bars', type=int, default=10)
        seed = request.args.get('seed', type=int, default=None)
        
        data = generate_ohlc_snippet(pattern, num_bars=num_bars, seed=seed)
        return jsonify({'pattern': pattern, 'bars': data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_dataset():
    """Generate a complete dataset."""
    try:
        config = request.json
        
        dataset_size = config.get('size', 100)
        seed_value = config.get('seed', 0)
        balance_categories = config.get('balance', True)
        output_name = config.get('filename', f'trading_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl')
        
        # Category weights
        if balance_categories:
            pine_weight = price_weight = inst_weight = 33.33
        else:
            pine_weight = config.get('pine_weight', 30)
            price_weight = config.get('price_weight', 40)
            inst_weight = config.get('inst_weight', 30)
        
        # Setup seed
        actual_seed = seed_value if seed_value > 0 else random.randint(1, 999999)
        random.seed(actual_seed)
        
        distribution = {
            'pinescript': int(dataset_size * pine_weight / 100),
            'price_action': int(dataset_size * price_weight / 100),
            'institutional': int(dataset_size * inst_weight / 100)
        }
        
        generators = {
            'pinescript': generate_pinescript,
            'price_action': generate_price_action,
            'institutional': generate_institutional
        }
        
        # Generate samples
        samples = []
        progress = []
        
        for category, count in distribution.items():
            for i in range(count):
                sample_seed = random.randint(0, 1000000)
                data = generators[category](seed=sample_seed)
                
                example = TrainingExample(
                    id=str(uuid.uuid4()),
                    instruction=data['instruction'],
                    response=data['response'],
                    pattern_type=data['pattern_type'],
                    timeframe=data.get('timeframe'),
                    seed=sample_seed,
                    metadata=data.get('metadata', {})
                )
                samples.append(example.model_dump())
        
        # Shuffle and save
        random.shuffle(samples)
        output_path = Path("datasets") / output_name
        
        with jsonlines.open(output_path, mode='w') as writer:
            writer.write_all(samples)
        
        return jsonify({
            'success': True,
            'samples_generated': len(samples),
            'filename': output_name,
            'path': str(output_path),
            'seed_used': actual_seed,
            'distribution': distribution
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all generated datasets."""
    try:
        datasets_dir = Path("datasets")
        datasets = []
        
        for file_path in datasets_dir.glob("*.jsonl"):
            stat = file_path.stat()
            
            # Count lines
            with open(file_path, 'r') as f:
                line_count = sum(1 for _ in f)
            
            datasets.append({
                'name': file_path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'samples': line_count,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return jsonify({'datasets': sorted(datasets, key=lambda x: x['modified'], reverse=True)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/<filename>', methods=['GET'])
def download_dataset(filename):
    """Download a specific dataset."""
    try:
        file_path = Path("datasets") / filename
        if not file_path.exists():
            return jsonify({'error': 'Dataset not found'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_dataset():
    """Validate a dataset file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        errors = []
        valid_count = 0
        
        for i, line in enumerate(file.stream):
            try:
                import json
                obj = json.loads(line)
                TrainingExample(**obj)
                valid_count += 1
            except Exception as e:
                errors.append({
                    'line': i + 1,
                    'error': str(e)
                })
        
        return jsonify({
            'valid': len(errors) == 0,
            'valid_count': valid_count,
            'error_count': len(errors),
            'errors': errors[:50]  # Return first 50 errors
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Trading Dataset Generator API")
    print("=" * 80)
    print("API running at: http://localhost:5000")
    print("Frontend: Open index.html in your browser")
    print("=" * 80)
    app.run(debug=True, port=5000)
