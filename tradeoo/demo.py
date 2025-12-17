"""Quick demo script to generate and display samples."""
import json
from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional
from src.generators.ohlc import generate_ohlc_snippet

def main():
    print("=" * 80)
    print("TRADING DATASET GENERATOR - DEMO")
    print("=" * 80)
    
    # PineScript Example
    print("\n1. PINESCRIPT STRATEGY")
    print("-" * 80)
    pine = generate_pinescript(seed=42)
    print(f"Instruction: {pine['instruction']}")
    print(f"\nResponse:\n{pine['response']}")
    
    # Price Action Example
    print("\n\n2. PRICE ACTION ANALYSIS")
    print("-" * 80)
    price = generate_price_action(seed=123)
    print(f"Instruction: {price['instruction']}")
    print(f"\nResponse: {price['response']}")
    
    # Institutional Flow Example
    print("\n\n3. INSTITUTIONAL FLOW")
    print("-" * 80)
    inst = generate_institutional(seed=456)
    print(f"Instruction: {inst['instruction']}")
    print(f"\nResponse: {inst['response']}")
    
    # OHLC Example
    print("\n\n4. SYNTHETIC OHLC DATA")
    print("-" * 80)
    ohlc = generate_ohlc_snippet("breakout", num_bars=10, seed=789)
    print(f"Pattern: Breakout (10 bars)")
    print(f"\nFirst 3 bars:")
    for i, bar in enumerate(ohlc[:3]):
        print(f"  Bar {i+1}: O={bar['open']:.2f} H={bar['high']:.2f} "
              f"L={bar['low']:.2f} C={bar['close']:.2f} V={bar['volume']}")
    
    print("\n" + "=" * 80)
    print("Demo complete! Run 'python cli.py generate --size 100' for full dataset")
    print("=" * 80)

if __name__ == "__main__":
    main()
