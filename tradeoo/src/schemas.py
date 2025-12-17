"""Data schemas for trading dataset generator."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TrainingExample(BaseModel):
    """Schema for a single training example."""
    id: str = Field(..., description="Unique identifier")
    instruction: str = Field(..., description="Input instruction/question")
    response: str = Field(..., description="Expected output/answer")
    pattern_type: str = Field(..., description="Type: pinescript|price_action|institutional|ohlc")
    timeframe: Optional[str] = Field(None, description="e.g., 1m, 5m, 1h, 1D")
    ticker: Optional[str] = Field(None, description="Stock/crypto ticker")
    source: Literal["synthetic", "real"] = Field("synthetic", description="Data source")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Quality confidence score")
    language: str = Field("en", description="Language code")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

class OHLCBar(BaseModel):
    """Single OHLC bar."""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
