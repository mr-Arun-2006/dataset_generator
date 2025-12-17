"""Institutional flow (FII/DII) generator."""
import random
from typing import Dict

TEMPLATES = [
    {
        "name": "FII_Buying",
        "instruction": "Analyze FII flow: bought ₹{fii_buy}Cr, DII sold ₹{dii_sell}Cr on {date}",
        "response": "FII net buying of ₹{fii_buy}Cr vs DII selling of ₹{dii_sell}Cr indicates foreign institutional interest. Net flow: +₹{net_flow}Cr. Sentiment: {sentiment}. Typically supports {market_action}. Sectors: {sectors}. Watch for continuation if FII buying sustains 3+ days. Reversal risk if DIIs turn buyers or FII flow reverses."
    },
    {
        "name": "DII_Support",
        "instruction": "Interpret DII buying ₹{dii_buy}Cr, FII selling ₹{fii_sell}Cr",
        "response": "DII buying ₹{dii_buy}Cr absorbing FII selling of ₹{fii_sell}Cr shows domestic institutional support. Net: {net_flow}Cr. This often stabilizes markets during FII outflows. Sentiment: {sentiment}. Suggests {market_action}. DIIs typically support large-caps and PSUs. Monitor if FII selling accelerates beyond DII capacity."
    },
    {
        "name": "Dual_Selling",
        "instruction": "Assess both FII sold ₹{fii_sell}Cr and DII sold ₹{dii_sell}Cr",
        "response": "Combined institutional selling: FII -₹{fii_sell}Cr, DII -₹{dii_sell}Cr. Total outflow: ₹{total_outflow}Cr. Sentiment: {sentiment}. Indicates {market_action}. Retail unlikely to absorb this pressure. Expect volatility and downside. Look for support at key levels. Reversal needs institutional flow to turn positive."
    },
    {
        "name": "Dual_Buying",
        "instruction": "Evaluate FII bought ₹{fii_buy}Cr, DII bought ₹{dii_buy}Cr",
        "response": "Strong institutional buying: FII +₹{fii_buy}Cr, DII +₹{dii_buy}Cr. Total inflow: ₹{total_inflow}Cr. Sentiment: {sentiment}. Signals {market_action}. Broad-based rally likely across sectors. Momentum can sustain with continued flows. Entry: on pullbacks. Exit: if flows reverse or diverge."
    },
    {
        "name": "Mixed_Flow",
        "instruction": "Analyze mixed flow: FII {fii_action} ₹{fii_amt}Cr, DII {dii_action} ₹{dii_amt}Cr on {sector} sector",
        "response": "{sector} sector flows: FII {fii_action} ₹{fii_amt}Cr, DII {dii_action} ₹{dii_amt}Cr. Net: ₹{net_flow}Cr. Sentiment: {sentiment}. Divergence suggests {market_action}. FII prefer growth/momentum, DII prefer value/defensives. Sector rotation likely. Watch for convergence or acceleration in one direction."
    }
]

def generate_institutional(seed: int = None) -> Dict[str, str]:
    """Generate institutional flow analysis."""
    if seed is not None:
        random.seed(seed)
    
    template = random.choice(TEMPLATES)
    
    fii_buy = round(random.uniform(500, 5000), 0)
    fii_sell = round(random.uniform(500, 5000), 0)
    dii_buy = round(random.uniform(300, 4000), 0)
    dii_sell = round(random.uniform(300, 4000), 0)
    
    fii_action = random.choice(["bought", "sold"])
    dii_action = random.choice(["bought", "sold"])
    fii_amt = fii_buy if fii_action == "bought" else fii_sell
    dii_amt = dii_buy if dii_action == "bought" else dii_sell
    
    net_flow = fii_buy - dii_sell if "FII_Buying" in template["name"] else dii_buy - fii_sell
    total_outflow = fii_sell + dii_sell
    total_inflow = fii_buy + dii_buy
    
    sentiment_map = {
        "FII_Buying": "Bullish",
        "DII_Support": "Cautiously Bullish",
        "Dual_Selling": "Bearish",
        "Dual_Buying": "Strongly Bullish",
        "Mixed_Flow": "Neutral to Mixed"
    }
    
    action_map = {
        "FII_Buying": "upside in growth stocks",
        "DII_Support": "range-bound consolidation",
        "Dual_Selling": "correction or downtrend",
        "Dual_Buying": "strong rally across indices",
        "Mixed_Flow": "sector-specific moves"
    }
    
    params = {
        "fii_buy": int(fii_buy),
        "fii_sell": int(fii_sell),
        "dii_buy": int(dii_buy),
        "dii_sell": int(dii_sell),
        "fii_action": fii_action,
        "dii_action": dii_action,
        "fii_amt": int(fii_amt),
        "dii_amt": int(dii_amt),
        "net_flow": int(net_flow),
        "total_outflow": int(total_outflow),
        "total_inflow": int(total_inflow),
        "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "sector": random.choice(["IT", "Banking", "Pharma", "Auto", "Metal", "FMCG"]),
        "sectors": ", ".join(random.sample(["IT", "Banking", "Pharma", "Auto", "Energy"], 2)),
        "sentiment": sentiment_map.get(template["name"], "Mixed"),
        "market_action": action_map.get(template["name"], "mixed moves")
    }
    
    instruction = template["instruction"].format(**params)
    response = template["response"].format(**params)
    
    return {
        "instruction": instruction,
        "response": response,
        "pattern_type": "institutional",
        "metadata": {"template": template["name"], "params": params}
    }
