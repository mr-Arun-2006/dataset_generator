"""Simple test without heavy dependencies."""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional

# Generate 3 samples
samples = []

print("Generating samples...")
samples.append(generate_pinescript(seed=1))
samples.append(generate_price_action(seed=2))
samples.append(generate_institutional(seed=3))

# Save to file
output_file = "datasets/test_samples.jsonl"
os.makedirs("datasets", exist_ok=True)

with open(output_file, 'w') as f:
    for sample in samples:
        # Add required fields
        sample['id'] = f"test-{len(samples)}"
        sample['source'] = 'synthetic'
        sample['confidence'] = 1.0
        sample['language'] = 'en'
        f.write(json.dumps(sample) + '\n')

print(f"✓ Generated {len(samples)} samples → {output_file}")

# Display samples
print("\n" + "="*80)
for i, sample in enumerate(samples, 1):
    print(f"\nSample {i}: {sample['pattern_type'].upper()}")
    print("-"*80)
    print(f"Instruction: {sample['instruction'][:100]}...")
    print(f"Response: {sample['response'][:150]}...")

print("\n" + "="*80)
print("✓ Test complete!")
