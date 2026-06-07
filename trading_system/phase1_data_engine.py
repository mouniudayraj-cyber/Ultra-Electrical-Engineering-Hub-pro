"""
🧠 INSTITUTIONAL AI TRADING SYSTEM - PHASE 1
DATA ENGINE (Market Brain Input System)

Real-time + historical data pipeline
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Tuple
import numpy as np
from abc import ABC, abstractmethod

# ==================== ENUMS ====================

class TimeFrame(Enum):
    """Trading timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

class DataSource(Enum):
    """Data providers"""
    PRICE = "price_data"
    OPTIONS = "options_data"
    DERIVATIVES = "derivatives_data"
    INSTITUTIONAL = "institutional_flow"
    EXTERNAL = "external_data"

# ==================== DATA MODELS ====================

@dataclass
class OHLCV:
    """OHLCV Candle structure"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def __post_init__(self):
        self.hl_range = self.high - self.low
        self.body = abs(self.close - self.open)
        self.upper_wick = self.high - max(self.open, self.close)
        self.lower_wick = min(self.open, self.close) - self.low
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "o": self.open,
            "h": self.high,
            "l": self.low,
            "c": self.close,
            "v": self.volume
        }

@dataclass
class DerivativesData:
    """Options & Futures data"""
    timestamp: datetime
    symbol: str
    open_interest: int
    iv_current: float  # Current Implied Volatility %
    iv_change: float   # IV change from previous
    put_call_ratio: float
    max_pain_zone: float
    gamma_pressure_zones: Dict[str, float]  # {"call": price, "put": price}
    pcr_trend: str  # "bullish" / "bearish" / "neutral"
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "oi": self.open_interest,
            "iv": self.iv_current,
            "pcr": self.put_call_ratio,
            "max_pain": self.max_pain_zone,
            "pcr_trend": self.pcr_trend
        }

@dataclass
class InstitutionalFlow:
    """FII/DII and smart money flow"""
    timestamp: datetime
    fii_net_flow: float  # Million USD
    dii_net_flow: float
    fii_trend: str  # "buying" / "selling" / "accumulating"
    index_futures_net: int
    smart_money_indicator: float  # -1 to +1
    flow_strength: int  # 1-10 scale
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "fii_flow": self.fii_net_flow,
            "dii_flow": self.dii_net_flow,
            "fii_trend": self.fii_trend,
            "smart_money": self.smart_money_indicator
        }

@dataclass
class NewsData:
    """Market news and sentiment"""
    timestamp: datetime
    title: str
    sentiment: str  # "positive" / "negative" / "neutral"
    sentiment_score: float  # -1 to +1
    impact_level: str  # "high" / "medium" / "low"
    relevant_symbols: List[str]
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "sentiment": self.sentiment,
            "impact": self.impact_level
        }

# ==================== DATA CACHE SYSTEM ====================

class DataCache:
    """In-memory cache for real-time data (Redis-like)"""
    
    def __init__(self, max_candles: int = 1000):
        self.candles: Dict[str, List[OHLCV]] = {}
        self.derivatives: Dict[str, DerivativesData] = {}
        self.institutional: Optional[InstitutionalFlow] = None
        self.news: List[NewsData] = []
        self.max_candles = max_candles
    
    def add_candle(self, symbol: str, candle: OHLCV) -> None:
        """Add OHLCV candle to cache"""
        if symbol not in self.candles:
            self.candles[symbol] = []
        
        self.candles[symbol].append(candle)
        
        # Keep only recent candles
        if len(self.candles[symbol]) > self.max_candles:
            self.candles[symbol] = self.candles[symbol][-self.max_candles:]
    
    def get_candles(self, symbol: str, limit: int = 100) -> List[OHLCV]:
        """Get last N candles"""
        if symbol not in self.candles:
            return []
        return self.candles[symbol][-limit:]
    
    def update_derivatives(self, data: DerivativesData) -> None:
        """Update derivatives data"""
        self.derivatives[data.symbol] = data
    
    def update_institutional_flow(self, data: InstitutionalFlow) -> None:
        """Update institutional flow data"""
        self.institutional = data
    
    def add_news(self, news: NewsData) -> None:
        """Add news item"""
        self.news.append(news)
        # Keep last 100 news items
        if len(self.news) > 100:
            self.news = self.news[-100:]
    
    def get_latest_news(self, minutes: int = 60) -> List[NewsData]:
        """Get recent news"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [n for n in self.news if n.timestamp > cutoff]

# ==================== DATA FETCHER (ABSTRACTION) ====================

class DataFetcher(ABC):
    """Abstract data fetcher for different sources"""
    
    @abstractmethod
    async def fetch_candles(self, symbol: str, timeframe: TimeFrame) -> List[OHLCV]:
        pass
    
    @abstractmethod
    async def fetch_derivatives(self, symbol: str) -> DerivativesData:
        pass
    
    @abstractmethod
    async def stream_live_data(self, symbol: str, callback) -> None:
        pass

# ==================== ZERODHA INTEGRATION (INDIA) ====================

class ZerodhaFetcher(DataFetcher):
    """Fetch data from Zerodha Kite API"""
    
    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token
        # In production: from kiteconnect import KiteConnect
        # self.kite = KiteConnect(api_key=api_key)
        # self.kite.set_access_token(access_token)
    
    async def fetch_candles(self, symbol: str, timeframe: TimeFrame, limit: int = 500) -> List[OHLCV]:
        """Fetch historical candles from Zerodha"""
        # Simulated implementation
        candles = []
        base_time = datetime.now()
        base_price = 50000  # Example: Nifty 50
        
        for i in range(limit):
            timestamp = base_time - timedelta(minutes=int(timeframe.value[:-1]) * (limit - i))
            noise = np.random.randn() * 100
            candles.append(OHLCV(
                timestamp=timestamp,
                open=base_price + noise,
                high=base_price + noise + abs(np.random.randn() * 50),
                low=base_price + noise - abs(np.random.randn() * 50),
                close=base_price + noise,
                volume=int(1000000 + np.random.randn() * 100000)
            ))
        
        return sorted(candles, key=lambda x: x.timestamp)
    
    async def fetch_derivatives(self, symbol: str) -> DerivativesData:
        """Fetch derivatives data"""
        return DerivativesData(
            timestamp=datetime.now(),
            symbol=symbol,
            open_interest=np.random.randint(100000000, 500000000),
            iv_current=25 + np.random.randn() * 5,
            iv_change=np.random.randn() * 0.5,
            put_call_ratio=1.2 + np.random.randn() * 0.2,
            max_pain_zone=50000,
            gamma_pressure_zones={
                "call": 50200,
                "put": 49800
            },
            pcr_trend="bullish" if np.random.rand() > 0.5 else "bearish"
        )
    
    async def stream_live_data(self, symbol: str, callback) -> None:
        """Stream live WebSocket data"""
        # Simulated streaming
        while True:
            await asyncio.sleep(1)
            candle = OHLCV(
                timestamp=datetime.now(),
                open=50000 + np.random.randn() * 50,
                high=50000 + np.random.randn() * 100,
                low=50000 + np.random.randn() * 100,
                close=50000 + np.random.randn() * 50,
                volume=int(np.random.randn() * 100000)
            )
            await callback(candle)

# ==================== DATA PIPELINE ====================

class DataPipeline:
    """Main data collection pipeline"""
    
    def __init__(self, fetcher: DataFetcher, cache: DataCache):
        self.fetcher = fetcher
        self.cache = cache
        self.is_running = False
    
    async def initialize_historical_data(self, symbols: List[str]) -> None:
        """Load historical data for all timeframes"""
        print("📊 Loading historical data...")
        
        for symbol in symbols:
            for tf in TimeFrame:
                candles = await self.fetcher.fetch_candles(symbol, tf)
                for candle in candles:
                    self.cache.add_candle(f"{symbol}_{tf.value}", candle)
                print(f"✅ Loaded {len(candles)} candles for {symbol} {tf.value}")
    
    async def start_live_streaming(self, symbols: List[str]) -> None:
        """Start live data streaming"""
        print("🔴 Starting live data stream...")
        self.is_running = True
        
        async def handle_candle(candle):
            for symbol in symbols:
                self.cache.add_candle(f"{symbol}_1m", candle)
        
        for symbol in symbols:
            await self.fetcher.stream_live_data(symbol, handle_candle)
    
    async def fetch_derivatives_periodic(self, symbols: List[str], interval_seconds: int = 60) -> None:
        """Fetch derivatives data periodically"""
        while self.is_running:
            for symbol in symbols:
                data = await self.fetcher.fetch_derivatives(symbol)
                self.cache.update_derivatives(data)
            
            await asyncio.sleep(interval_seconds)
    
    def get_market_snapshot(self, symbol: str) -> Dict:
        """Get current market snapshot"""
        candles_1m = self.cache.get_candles(f"{symbol}_1m", 5)
        candles_5m = self.cache.get_candles(f"{symbol}_5m", 5)
        derivatives = self.cache.derivatives.get(symbol)
        
        if not candles_1m:
            return {}
        
        latest = candles_1m[-1]
        
        return {
            "symbol": symbol,
            "timestamp": latest.timestamp.isoformat(),
            "current_price": latest.close,
            "1m_candles": [c.to_dict() for c in candles_1m],
            "5m_candles": [c.to_dict() for c in candles_5m],
            "derivatives": derivatives.to_dict() if derivatives else None,
            "volatility": self._calculate_volatility(candles_5m)
        }
    
    @staticmethod
    def _calculate_volatility(candles: List[OHLCV]) -> float:
        """Calculate current volatility (ATR based)"""
        if len(candles) < 2:
            return 0
        
        tr_list = []
        for candle in candles:
            tr = max(
                candle.high - candle.low,
                abs(candle.high - candles[candles.index(candle) - 1].close) if candles.index(candle) > 0 else 0,
                abs(candle.low - candles[candles.index(candle) - 1].close) if candles.index(candle) > 0 else 0
            )
            tr_list.append(tr)
        
        atr = sum(tr_list) / len(tr_list) if tr_list else 0
        return round(atr, 2)

print("✅ PHASE 1: DATA ENGINE - READY")
