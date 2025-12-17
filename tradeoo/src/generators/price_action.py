"""Price action pattern generator."""
import random
import numpy as np
from typing import Dict, List

TEMPLATES = [
    {
        "name": "Retest",
        "instruction": "Explain the retest pattern at {price} level on {timeframe} timeframe",
        "response": "A retest occurs when price breaks through a key level at {price}, pulls back to test it as new support/resistance, and then continues in the breakout direction. This validates the level flip. On {timeframe}, look for: 1) Initial break with volume, 2) Pullback with lower volume, 3) Bounce/rejection at the level, 4) Continuation move. Entry: on bounce confirmation. Stop: below/above the retested level."
    },
    {
        "name": "Breakout",
        "instruction": "Describe a breakout pattern from {pattern_type} at {price}",
        "response": "Breakout from {pattern_type} at {price}: Price consolidates in a defined range, then breaks out with increased volume. Valid breakout requires: 1) Clear consolidation period (min 3 touches), 2) Volume spike on break (1.5x+ average), 3) Close beyond level, 4) No immediate reversal. Entry: on breakout candle close or retest. Target: measured move = range height. Stop: inside the pattern."
    },
    {
        "name": "False_Breakout",
        "instruction": "Identify false breakout characteristics at {level}",
        "response": "False breakout (fakeout) at {level}: Price briefly breaks the level but quickly reverses, trapping breakout traders. Signs: 1) Breakout with low/declining volume, 2) Long wick beyond level, 3) Close back inside range, 4) Rapid reversal within 1-3 bars. This often precedes strong move in opposite direction. Trade the reversal: enter when price re-enters range, stop beyond the false break high/low."
    },
    {
        "name": "Pin_Bar",
        "instruction": "Analyze pin bar formation at {location}",
        "response": "Pin bar at {location}: Reversal candlestick with long wick (2-3x body) and small body near opposite end. Bullish pin: long lower wick, small body at top (rejection of lows). Bearish pin: long upper wick, small body at bottom (rejection of highs). Strongest at key levels. Entry: above/below pin bar. Stop: beyond the wick. Target: recent swing high/low."
    },
    {
        "name": "Engulfing",
        "instruction": "Explain {direction} engulfing pattern at {price}",
        "response": "{direction} engulfing at {price}: Two-candle reversal where second candle completely engulfs the first. Bullish: red candle followed by larger green candle that opens below prior close and closes above prior open. Bearish: opposite. Signals momentum shift. Stronger with: 1) Prior trend, 2) At key level, 3) Volume increase. Entry: on engulfing close. Stop: beyond engulfing low/high."
    },
    {
        "name": "Higher_Highs_Higher_Lows",
        "instruction": "Describe HH/HL uptrend structure from {start} to {end}",
        "response": "HH/HL uptrend from {start} to {end}: Each swing high exceeds the prior high, each swing low exceeds the prior low. This confirms bullish trend structure. Trade: buy pullbacks to rising support (HL), target new HH. Trend intact while HL pattern holds. Broken if: price makes lower low (LL), signaling potential reversal. Use trendline connecting HLs for dynamic support."
    },
    {
        "name": "Lower_Highs_Lower_Lows",
        "instruction": "Identify LH/LL downtrend from {start} to {end}",
        "response": "LH/LL downtrend from {start} to {end}: Each swing high is lower than prior, each swing low is lower. Confirms bearish structure. Trade: sell rallies to descending resistance (LH), target new LL. Trend valid while LH pattern continues. Reversal signal: higher high (HH) formation. Draw trendline connecting LHs for dynamic resistance. Avoid longs until structure breaks."
    },
    {
        "name": "Order_Block",
        "instruction": "Explain order block at {price} on {timeframe}",
        "response": "Order block at {price} on {timeframe}: Last bullish/bearish candle before strong impulsive move, representing institutional accumulation/distribution. Bullish OB: last green candle before sharp up-move (buy orders). Bearish OB: last red candle before sharp down-move (sell orders). Price often returns to these zones for liquidity. Entry: on retest of OB. Stop: beyond the block. High probability at untested OBs."
    }
]

def generate_price_action(seed: int = None) -> Dict[str, str]:
    """Generate price action explanation."""
    if seed is not None:
        random.seed(seed)
    
    template = random.choice(TEMPLATES)
    
    params = {
        "price": round(random.uniform(100, 500), 2),
        "timeframe": random.choice(["5m", "15m", "1h", "4h", "1D"]),
        "pattern_type": random.choice(["triangle", "rectangle", "channel", "wedge"]),
        "level": round(random.uniform(100, 500), 2),
        "location": random.choice(["support", "resistance", "key level", "trendline"]),
        "direction": random.choice(["Bullish", "Bearish"]),
        "start": round(random.uniform(100, 300), 2),
        "end": round(random.uniform(300, 500), 2),
    }
    
    instruction = template["instruction"].format(**params)
    response = template["response"].format(**params)
    
    return {
        "instruction": instruction,
        "response": response,
        "pattern_type": "price_action",
        "timeframe": params.get("timeframe"),
        "metadata": {"template": template["name"], "params": params}
    }
