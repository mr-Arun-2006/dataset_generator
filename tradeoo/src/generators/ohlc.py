"""Synthetic OHLC generator for pattern illustration."""
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

def generate_ohlc_snippet(pattern: str, num_bars: int = 10, seed: int = None) -> List[Dict]:
    """Generate synthetic OHLC bars illustrating a specific pattern."""
    if seed is not None:
        np.random.seed(seed)
    
    base_price = np.random.uniform(100, 500)
    bars = []
    
    if pattern == "uptrend":
        bars = _generate_uptrend(base_price, num_bars)
    elif pattern == "downtrend":
        bars = _generate_downtrend(base_price, num_bars)
    elif pattern == "breakout":
        bars = _generate_breakout(base_price, num_bars)
    elif pattern == "pin_bar":
        bars = _generate_pin_bar(base_price, num_bars)
    elif pattern == "engulfing":
        bars = _generate_engulfing(base_price, num_bars)
    else:
        bars = _generate_random_walk(base_price, num_bars)
    
    return bars

def _generate_uptrend(base: float, n: int) -> List[Dict]:
    """Generate uptrending OHLC bars."""
    bars = []
    current_price = base
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    for i in range(n):
        open_price = current_price
        close_price = open_price * np.random.uniform(1.002, 1.015)
        high_price = close_price * np.random.uniform(1.001, 1.008)
        low_price = open_price * np.random.uniform(0.995, 0.999)
        
        bars.append({
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(np.random.uniform(10000, 50000))
        })
        current_price = close_price
    
    return bars

def _generate_downtrend(base: float, n: int) -> List[Dict]:
    """Generate downtrending OHLC bars."""
    bars = []
    current_price = base
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    for i in range(n):
        open_price = current_price
        close_price = open_price * np.random.uniform(0.985, 0.998)
        high_price = open_price * np.random.uniform(1.001, 1.005)
        low_price = close_price * np.random.uniform(0.992, 0.999)
        
        bars.append({
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(np.random.uniform(10000, 50000))
        })
        current_price = close_price
    
    return bars

def _generate_breakout(base: float, n: int) -> List[Dict]:
    """Generate consolidation followed by breakout."""
    bars = []
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    # Consolidation phase
    for i in range(n - 3):
        open_price = base * np.random.uniform(0.998, 1.002)
        close_price = base * np.random.uniform(0.998, 1.002)
        high_price = max(open_price, close_price) * np.random.uniform(1.001, 1.003)
        low_price = min(open_price, close_price) * np.random.uniform(0.997, 0.999)
        
        bars.append({
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(np.random.uniform(10000, 30000))
        })
    
    # Breakout bars
    for i in range(n - 3, n):
        open_price = base if i == n - 3 else bars[-1]["close"]
        close_price = open_price * 1.02
        high_price = close_price * 1.005
        low_price = open_price * 0.998
        
        bars.append({
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(np.random.uniform(50000, 100000))
        })
    
    return bars

def _generate_pin_bar(base: float, n: int) -> List[Dict]:
    """Generate bars with pin bar at the end."""
    bars = _generate_random_walk(base, n - 1)
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    # Add bullish pin bar
    last_close = bars[-1]["close"] if bars else base
    open_price = last_close
    close_price = open_price * 1.005
    high_price = close_price * 1.002
    low_price = open_price * 0.97  # Long lower wick
    
    bars.append({
        "timestamp": (start_time + timedelta(minutes=(n-1)*5)).isoformat(),
        "open": round(open_price, 2),
        "high": round(high_price, 2),
        "low": round(low_price, 2),
        "close": round(close_price, 2),
        "volume": int(np.random.uniform(30000, 60000))
    })
    
    return bars

def _generate_engulfing(base: float, n: int) -> List[Dict]:
    """Generate bars with engulfing pattern."""
    bars = _generate_random_walk(base, n - 2)
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    last_close = bars[-1]["close"] if bars else base
    
    # Small bearish candle
    open1 = last_close
    close1 = open1 * 0.995
    bars.append({
        "timestamp": (start_time + timedelta(minutes=(n-2)*5)).isoformat(),
        "open": round(open1, 2),
        "high": round(open1 * 1.002, 2),
        "low": round(close1 * 0.998, 2),
        "close": round(close1, 2),
        "volume": int(np.random.uniform(20000, 40000))
    })
    
    # Large bullish engulfing candle
    open2 = close1 * 0.998
    close2 = open1 * 1.01
    bars.append({
        "timestamp": (start_time + timedelta(minutes=(n-1)*5)).isoformat(),
        "open": round(open2, 2),
        "high": round(close2 * 1.003, 2),
        "low": round(open2 * 0.997, 2),
        "close": round(close2, 2),
        "volume": int(np.random.uniform(50000, 80000))
    })
    
    return bars

def _generate_random_walk(base: float, n: int) -> List[Dict]:
    """Generate random walk OHLC bars."""
    bars = []
    current_price = base
    start_time = datetime.now() - timedelta(minutes=n*5)
    
    for i in range(n):
        direction = np.random.choice([-1, 1])
        open_price = current_price
        close_price = open_price * (1 + direction * np.random.uniform(0.002, 0.01))
        high_price = max(open_price, close_price) * np.random.uniform(1.001, 1.005)
        low_price = min(open_price, close_price) * np.random.uniform(0.995, 0.999)
        
        bars.append({
            "timestamp": (start_time + timedelta(minutes=i*5)).isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": int(np.random.uniform(10000, 50000))
        })
        current_price = close_price
    
    return bars
