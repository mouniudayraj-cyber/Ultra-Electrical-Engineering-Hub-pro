"""
🧠 INSTITUTIONAL AI TRADING SYSTEM - PHASE 2
FEATURE ENGINE (Market Brain Intelligence Layer)

Extracts intelligent features from raw market data
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime
from enum import Enum

# ==================== FEATURE ENUMS ====================

class TrendStrength(Enum):
    VERY_WEAK = 1
    WEAK = 2
    NEUTRAL = 3
    STRONG = 4
    VERY_STRONG = 5

class VolumeSignal(Enum):
    VERY_LOW = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    VERY_HIGH = 2

# ==================== FEATURE OBJECTS ====================

@dataclass
class PriceFeatures:
    """Price-based technical features"""
    trend_strength: TrendStrength
    trend_direction: str  # "up" / "down" / "sideways"
    
    # Support/Resistance
    support_zone: float
    resistance_zone: float
    support_strength: float  # 0-1
    resistance_strength: float
    
    # Volatility
    atr_value: float
    atr_percent: float
    volatility_regime: str  # "high" / "normal" / "low"
    
    # Momentum
    rsi: float
    macd_histogram: float
    momentum_direction: str
    
    def to_dict(self):
        return {
            "trend_strength": self.trend_strength.name,
            "trend_direction": self.trend_direction,
            "support": round(self.support_zone, 2),
            "resistance": round(self.resistance_zone, 2),
            "atr_percent": round(self.atr_percent, 2),
            "volatility": self.volatility_regime,
            "rsi": round(self.rsi, 2),
            "momentum": self.momentum_direction
        }

@dataclass
class VolumeFeatures:
    """Volume-based technical features"""
    volume_signal: VolumeSignal
    volume_trend: str  # "increasing" / "decreasing" / "stable"
    
    # Divergences
    price_volume_divergence: bool
    divergence_strength: float  # 0-1
    
    # Accumulation
    accumulation_score: float  # -1 to +1
    on_balance_volume: float
    
    def to_dict(self):
        return {
            "volume_signal": self.volume_signal.name,
            "trend": self.volume_trend,
            "divergence": self.price_volume_divergence,
            "divergence_strength": round(self.divergence_strength, 2),
            "accumulation": round(self.accumulation_score, 2)
        }

@dataclass
class OptionsFeatures:
    """Options market features"""
    oi_buildup_direction: str  # "calls" / "puts" / "balanced"
    oi_buildup_strength: float  # 0-1
    pcr_signal: str  # "bullish" / "bearish" / "neutral"
    pcr_value: float
    max_pain_proximity: float  # Distance to max pain in %
    gamma_squeeze_zone: float  # 0-1, proximity to gamma pressure
    iv_rank: float  # 0-100
    iv_percentile: float
    implied_move: float
    
    def to_dict(self):
        return {
            "oi_buildup": self.oi_buildup_direction,
            "oi_strength": round(self.oi_buildup_strength, 2),
            "pcr_signal": self.pcr_signal,
            "gamma_squeeze": round(self.gamma_squeeze_zone, 2),
            "implied_move": round(self.implied_move, 2)
        }

@dataclass
class LiquidityFeatures:
    """Liquidity and smart money features"""
    sl_zone_liquidity: Dict[str, float]  # {"above": price, "below": price}
    wick_rejection_signal: str  # "strong" / "moderate" / "weak"
    breakout_failure_probability: float  # 0-1
    liquidity_sweep_detected: bool
    sweep_direction: str  # "up" / "down" / "none"
    premium_distribution: float  # -1 to +1
    
    def to_dict(self):
        return {
            "stop_loss_zones": self.sl_zone_liquidity,
            "wick_rejection": self.wick_rejection_signal,
            "breakout_fail_prob": round(self.breakout_failure_probability, 2),
            "liquidity_sweep": self.liquidity_sweep_detected,
            "sweep_direction": self.sweep_direction
        }

# ==================== FEATURE EXTRACTOR ====================

class FeatureExtractor:
    """Extract all features from price + volume data"""
    
    def __init__(self, period_short: int = 5, period_long: int = 20):
        self.period_short = period_short
        self.period_long = period_long
    
    # ========== PRICE FEATURES ==========
    
    def extract_price_features(self, closes: List[float], highs: List[float], lows: List[float]) -> PriceFeatures:
        """Extract price-based features"""
        
        # Trend analysis
        ema_short = self._calculate_ema(closes, self.period_short)
        ema_long = self._calculate_ema(closes, self.period_long)
        trend_direction = "up" if ema_short[-1] > ema_long[-1] else "down" if ema_short[-1] < ema_long[-1] else "sideways"
        
        # Trend strength
        trend_strength = self._calculate_trend_strength(closes)
        
        # Support/Resistance
        support, resistance = self._find_support_resistance(highs, lows)
        support_strength = self._calculate_zone_strength(lows, support)
        resistance_strength = self._calculate_zone_strength(highs, resistance)
        
        # Volatility (ATR)
        atr = self._calculate_atr(highs, lows, closes, period=14)
        atr_percent = (atr[-1] / closes[-1]) * 100
        volatility_regime = "high" if atr_percent > 1.5 else "low" if atr_percent < 0.5 else "normal"
        
        # Momentum
        rsi = self._calculate_rsi(closes, period=14)
        macd_hist = self._calculate_macd_histogram(closes)
        momentum_direction = "bullish" if macd_hist[-1] > 0 else "bearish"
        
        return PriceFeatures(
            trend_strength=TrendStrength(int(trend_strength)),
            trend_direction=trend_direction,
            support_zone=support,
            resistance_zone=resistance,
            support_strength=support_strength,
            resistance_strength=resistance_strength,
            atr_value=atr[-1],
            atr_percent=atr_percent,
            volatility_regime=volatility_regime,
            rsi=rsi[-1],
            macd_histogram=macd_hist[-1],
            momentum_direction=momentum_direction
        )
    
    # ========== VOLUME FEATURES ==========
    
    def extract_volume_features(self, closes: List[float], volumes: List[float]) -> VolumeFeatures:
        """Extract volume-based features"""
        
        # Volume signal
        avg_vol = np.mean(volumes[-20:])
        current_vol = volumes[-1]
        vol_signal = VolumeSignal(int(min(2, max(-2, (current_vol - avg_vol) / (avg_vol * 0.1)))))
        
        # Volume trend
        vol_trend = "increasing" if volumes[-1] > np.mean(volumes[-5:-1]) else "decreasing"
        
        # Price-Volume divergence
        price_trend = "up" if closes[-1] > closes[-5] else "down"
        vol_trend_bool = "up" if volumes[-1] > np.mean(volumes[-5:-1]) else "down"
        price_vol_div = price_trend != vol_trend_bool
        divergence_strength = abs((closes[-1] - closes[-5]) / closes[-5]) - (abs(current_vol - avg_vol) / avg_vol)
        
        # Accumulation
        obv = self._calculate_obv(closes, volumes)
        acc_score = self._calculate_accumulation_score(closes, volumes)
        
        return VolumeFeatures(
            volume_signal=vol_signal,
            volume_trend=vol_trend,
            price_volume_divergence=price_vol_div,
            divergence_strength=max(0, divergence_strength),
            accumulation_score=acc_score,
            on_balance_volume=obv[-1]
        )
    
    # ========== OPTIONS FEATURES ==========
    
    def extract_options_features(self, pcr: float, oi: int, iv_current: float, iv_percentile: float, max_pain: float, current_price: float) -> OptionsFeatures:
        """Extract options market features"""
        
        # OI buildup
        oi_direction = "calls" if pcr < 1.0 else "puts" if pcr > 1.0 else "balanced"
        oi_strength = abs(1.0 - pcr) / 2.0  # Normalize to 0-1
        
        # PCR signal
        pcr_signal = "bullish" if pcr < 0.8 else "bearish" if pcr > 1.2 else "neutral"
        
        # Max pain proximity
        max_pain_dist = abs(current_price - max_pain) / current_price * 100
        max_pain_proximity = 1.0 - (max_pain_dist / 5.0)  # 5% proximity = full score
        
        # Gamma squeeze (simplified)
        gamma_squeeze = 1.0 - (max_pain_dist / 10.0)
        
        # Implied move
        implied_move = (iv_current / 100.0) * current_price / np.sqrt(252)  # Daily move
        
        return OptionsFeatures(
            oi_buildup_direction=oi_direction,
            oi_buildup_strength=oi_strength,
            pcr_signal=pcr_signal,
            pcr_value=pcr,
            max_pain_proximity=max(0, min(1, max_pain_proximity)),
            gamma_squeeze_zone=max(0, min(1, gamma_squeeze)),
            iv_rank=iv_percentile,
            iv_percentile=iv_percentile,
            implied_move=implied_move
        )
    
    # ========== LIQUIDITY FEATURES ==========
    
    def extract_liquidity_features(self, highs: List[float], lows: List[float], closes: List[float]) -> LiquidityFeatures:
        """Extract liquidity and smart money features"""
        
        # Stop loss zones
        recent_low = min(lows[-10:])
        recent_high = max(highs[-10:])
        sl_zones = {"below": recent_low * 0.99, "above": recent_high * 1.01}
        
        # Wick rejection
        wick_strength = self._analyze_wick_strength(highs, lows, closes)
        wick_signal = "strong" if wick_strength > 0.7 else "moderate" if wick_strength > 0.4 else "weak"
        
        # Breakout failure probability
        breakout_failure_prob = self._calculate_breakout_failure_prob(closes, highs, lows)
        
        # Liquidity sweep
        sweep_detected = wick_strength > 0.8
        sweep_dir = "up" if highs[-1] > max(highs[-10:-1]) else "down" if lows[-1] < min(lows[-10:-1]) else "none"
        
        # Premium distribution
        premium = 1.0 if closes[-1] > highs[-5] else -1.0 if closes[-1] < lows[-5] else 0.0
        
        return LiquidityFeatures(
            sl_zone_liquidity=sl_zones,
            wick_rejection_signal=wick_signal,
            breakout_failure_probability=breakout_failure_prob,
            liquidity_sweep_detected=sweep_detected,
            sweep_direction=sweep_dir,
            premium_distribution=premium
        )
    
    # ========== HELPER CALCULATIONS ==========
    
    @staticmethod
    def _calculate_ema(values: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        ema = []
        multiplier = 2 / (period + 1)
        ema.append(np.mean(values[:period]))
        
        for val in values[period:]:
            ema.append(val * multiplier + ema[-1] * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def _calculate_rsi(values: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        gains = [max(0, values[i] - values[i-1]) for i in range(1, len(values))]
        losses = [max(0, values[i-1] - values[i]) for i in range(1, len(values))]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return [rsi]
    
    @staticmethod
    def _calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate Average True Range"""
        atr = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            atr.append(tr)
        
        return [np.mean(atr[-period:])]
    
    @staticmethod
    def _calculate_macd_histogram(closes: List[float]) -> List[float]:
        """Calculate MACD histogram"""
        ema12 = FeatureExtractor._calculate_ema(closes, 12)
        ema26 = FeatureExtractor._calculate_ema(closes, 26)
        macd = np.array(ema12) - np.array(ema26)
        return macd[-1:].tolist()
    
    @staticmethod
    def _calculate_obv(closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate On-Balance Volume"""
        obv = [0]
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        return obv[-1:]
    
    @staticmethod
    def _find_support_resistance(highs: List[float], lows: List[float]) -> Tuple[float, float]:
        """Find support and resistance levels"""
        support = min(lows[-20:])
        resistance = max(highs[-20:])
        return support, resistance
    
    @staticmethod
    def _calculate_trend_strength(closes: List[float]) -> float:
        """Calculate trend strength 1-5"""
        trend_up = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
        trend_ratio = trend_up / len(closes)
        return 1 + (trend_ratio * 4)  # 1-5 scale
    
    @staticmethod
    def _calculate_zone_strength(values: List[float], zone: float) -> float:
        """Calculate how strong a zone is (touches)"""
        touches = sum(1 for v in values[-20:] if abs(v - zone) < zone * 0.01)
        return min(1.0, touches / 5.0)
    
    @staticmethod
    def _calculate_accumulation_score(closes: List[float], volumes: List[float]) -> float:
        """Calculate accumulation/distribution"""
        score = 0
        for i in range(len(closes) - 1):
            if closes[i+1] > closes[i] and volumes[i+1] > volumes[i]:
                score += 1
            elif closes[i+1] < closes[i] and volumes[i+1] > volumes[i]:
                score -= 1
        return score / len(closes) if closes else 0
    
    @staticmethod
    def _analyze_wick_strength(highs: List[float], lows: List[float], closes: List[float]) -> float:
        """Analyze wick strength/rejection"""
        wicks_up = [highs[i] - max(closes[i], closes[i-1]) for i in range(1, len(highs))]
        body_range = [abs(closes[i] - closes[i-1]) for i in range(1, len(closes))]
        wick_body_ratio = np.mean(wicks_up[-10:]) / (np.mean(body_range[-10:]) + 0.001)
        return min(1.0, wick_body_ratio / 2.0)
    
    @staticmethod
    def _calculate_breakout_failure_prob(closes: List[float], highs: List[float], lows: List[float]) -> float:
        """Calculate probability of breakout failure"""
        # Simple: if price went above but came back
        if len(closes) < 10:
            return 0.0
        recent_high = max(highs[-10:])
        failure_count = sum(1 for i in range(len(closes)-5, len(closes)) if closes[i] < recent_high * 0.99)
        return failure_count / 5.0

print("✅ PHASE 2: FEATURE ENGINE - READY")
