"""PineScript strategy generator."""
import random
from typing import Dict, List

TEMPLATES = [
    {
        "name": "EMA_Crossover",
        "instruction": "Write a PineScript v5 strategy for EMA crossover with {fast_len} and {slow_len} periods",
        "code": """//@version=5
strategy("EMA Crossover", overlay=true)
fastLen = input.int({fast_len}, "Fast EMA")
slowLen = input.int({slow_len}, "Slow EMA")
fastEMA = ta.ema(close, fastLen)
slowEMA = ta.ema(close, slowLen)
if ta.crossover(fastEMA, slowEMA)
    strategy.entry("Long", strategy.long)
if ta.crossunder(fastEMA, slowEMA)
    strategy.close("Long")
plot(fastEMA, color=color.blue)
plot(slowEMA, color=color.red)"""
    },
    {
        "name": "RSI_EMA",
        "instruction": "Create a PineScript v5 strategy combining RSI({rsi_len}) and EMA({ema_len}) with oversold at {oversold} and overbought at {overbought}",
        "code": """//@version=5
strategy("RSI + EMA Strategy", overlay=true)
rsiLen = input.int({rsi_len}, "RSI Length")
emaLen = input.int({ema_len}, "EMA Length")
rsiOversold = input.int({oversold}, "Oversold")
rsiOverbought = input.int({overbought}, "Overbought")
rsi = ta.rsi(close, rsiLen)
ema = ta.ema(close, emaLen)
longCondition = ta.crossover(rsi, rsiOversold) and close > ema
shortCondition = ta.crossunder(rsi, rsiOverbought) and close < ema
if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.entry("Short", strategy.short)"""
    },
    {
        "name": "Bollinger_Breakout",
        "instruction": "Write a PineScript v5 Bollinger Band breakout strategy with {bb_len} period and {bb_mult} standard deviations",
        "code": """//@version=5
strategy("BB Breakout", overlay=true)
length = input.int({bb_len}, "BB Length")
mult = input.float({bb_mult}, "BB Multiplier")
basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)
upper = basis + dev
lower = basis - dev
if ta.crossover(close, upper)
    strategy.entry("Long", strategy.long)
if ta.crossunder(close, lower)
    strategy.entry("Short", strategy.short)
plot(basis, color=color.orange)
plot(upper, color=color.red)
plot(lower, color=color.green)"""
    },
    {
        "name": "VWAP_Scalper",
        "instruction": "Create a PineScript v5 VWAP scalping strategy with {tp_pct}% take profit and {sl_pct}% stop loss",
        "code": """//@version=5
strategy("VWAP Scalper", overlay=true)
vwapValue = ta.vwap(close)
tpPercent = input.float({tp_pct}, "Take Profit %") / 100
slPercent = input.float({sl_pct}, "Stop Loss %") / 100
if ta.crossover(close, vwapValue)
    strategy.entry("Long", strategy.long)
    strategy.exit("Exit", "Long", profit=close * tpPercent, loss=close * slPercent)
if ta.crossunder(close, vwapValue)
    strategy.close("Long")
plot(vwapValue, color=color.blue, linewidth=2)"""
    },
    {
        "name": "Multi_Timeframe",
        "instruction": "Write a PineScript v5 multi-timeframe strategy using {htf} higher timeframe EMA({htf_len}) and current timeframe RSI({rsi_len})",
        "code": """//@version=5
strategy("MTF Strategy", overlay=true)
htfEmaLen = input.int({htf_len}, "HTF EMA Length")
htf = input.timeframe("{htf}", "Higher Timeframe")
rsiLen = input.int({rsi_len}, "RSI Length")
htfEMA = request.security(syminfo.tickerid, htf, ta.ema(close, htfEmaLen))
rsi = ta.rsi(close, rsiLen)
longCondition = close > htfEMA and rsi < 30
shortCondition = close < htfEMA and rsi > 70
if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.entry("Short", strategy.short)
plot(htfEMA, color=color.purple, linewidth=2)"""
    }
]

def generate_pinescript(seed: int = None) -> Dict[str, str]:
    """Generate a random PineScript strategy."""
    if seed is not None:
        random.seed(seed)
    
    template = random.choice(TEMPLATES)
    
    params = {
        "fast_len": random.randint(8, 21),
        "slow_len": random.randint(50, 200),
        "rsi_len": random.randint(10, 21),
        "ema_len": random.randint(20, 100),
        "oversold": random.randint(20, 35),
        "overbought": random.randint(65, 80),
        "bb_len": random.randint(15, 25),
        "bb_mult": round(random.uniform(1.5, 2.5), 1),
        "tp_pct": round(random.uniform(0.5, 3.0), 2),
        "sl_pct": round(random.uniform(0.3, 2.0), 2),
        "htf": random.choice(["15", "60", "240", "D"]),
        "htf_len": random.randint(20, 50),
    }
    
    instruction = template["instruction"].format(**params)
    response = template["code"].format(**params)
    
    return {
        "instruction": instruction,
        "response": response,
        "pattern_type": "pinescript",
        "metadata": {"template": template["name"], "params": params}
    }
