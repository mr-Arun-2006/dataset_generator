"""Main CLI interface for dataset generation."""
import click
import jsonlines
import uuid
from pathlib import Path
from typing import Optional
import random

from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional
from src.schemas import TrainingExample

@click.group()
def cli():
    """Trading Dataset Generator CLI."""
    pass

@cli.command()
@click.option('--size', default=1000, help='Number of samples to generate')
@click.option('--output', default='datasets/trading_dataset.jsonl', help='Output file path')
@click.option('--seed', default=None, type=int, help='Random seed for reproducibility')
@click.option('--balance', is_flag=True, help='Balance categories equally')
def generate(size: int, output: str, seed: Optional[int], balance: bool):
    """Generate a new dataset."""
    click.echo(f"Generating {size} samples...")
    
    if seed is not None:
        random.seed(seed)
    
    # Category distribution
    if balance:
        per_category = size // 3
        distribution = {
            'pinescript': per_category,
            'price_action': per_category,
            'institutional': size - 2 * per_category
        }
    else:
        distribution = {
            'pinescript': int(size * 0.3),
            'price_action': int(size * 0.4),
            'institutional': int(size * 0.3)
        }
    
    generators = {
        'pinescript': generate_pinescript,
        'price_action': generate_price_action,
        'institutional': generate_institutional
    }
    
    # Create output directory
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    
    samples = []
    for category, count in distribution.items():
        click.echo(f"  Generating {count} {category} samples...")
        for i in range(count):
            sample_seed = random.randint(0, 1000000) if seed is None else seed + i
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
    
    # Shuffle
    random.shuffle(samples)
    
    # Write JSONL
    with jsonlines.open(output, mode='w') as writer:
        writer.write_all(samples)
    
    click.echo(f"✓ Generated {len(samples)} samples → {output}")
    click.echo(f"  PineScript: {distribution['pinescript']}")
    click.echo(f"  Price Action: {distribution['price_action']}")
    click.echo(f"  Institutional: {distribution['institutional']}")

@cli.command()
@click.option('--input', required=True, help='Input JSONL file to validate')
def validate(input: str):
    """Validate an existing dataset."""
    click.echo(f"Validating {input}...")
    
    total = 0
    errors = []
    
    with jsonlines.open(input) as reader:
        for i, obj in enumerate(reader):
            total += 1
            try:
                TrainingExample(**obj)
            except Exception as e:
                errors.append(f"Line {i+1}: {str(e)}")
    
    if errors:
        click.echo(f"✗ Found {len(errors)} errors:")
        for err in errors[:10]:
            click.echo(f"  {err}")
    else:
        click.echo(f"✓ All {total} samples valid!")

@cli.command()
@click.option('--input', required=True, help='Input JSONL file')
def stats(input: str):
    """Show dataset statistics."""
    from collections import Counter
    
    pattern_counts = Counter()
    timeframe_counts = Counter()
    total = 0
    
    with jsonlines.open(input) as reader:
        for obj in reader:
            total += 1
            pattern_counts[obj.get('pattern_type', 'unknown')] += 1
            if obj.get('timeframe'):
                timeframe_counts[obj['timeframe']] += 1
    
    click.echo(f"Dataset Statistics for {input}")
    click.echo(f"  Total samples: {total}")
    click.echo(f"\n  Pattern distribution:")
    for pattern, count in pattern_counts.most_common():
        click.echo(f"    {pattern}: {count} ({count/total*100:.1f}%)")
    
    if timeframe_counts:
        click.echo(f"\n  Timeframe distribution:")
        for tf, count in timeframe_counts.most_common():
            click.echo(f"    {tf}: {count}")

if __name__ == '__main__':
    cli()
