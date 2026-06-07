"""
🧠 INSTITUTIONAL AI TRADING SYSTEM - PHASE 5
SIGNAL FUSION ENGINE (Final Decision System)

Combines all signals into final actionable trading signal
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
import numpy as np

# ==================== SIGNAL ENUMS ====================

class SignalQuality(Enum):
    EXCELLENT = "🟢 EXCELLENT (90-100%)"
    GOOD = "🟡 GOOD (70-90%)"
    FAIR = "🟠 FAIR (50-70%)"
    POOR = "🔴 POOR (<50%)"

# ==================== FINAL SIGNAL OUTPUT ====================

@dataclass
class FinalTradingSignal:
    """Complete actionable trading signal"""
    timestamp: datetime
    symbol: str
    
    # Direction
    direction_probability_up: float  # %
    direction_probability_down: float  # %
    predicted_direction: str  # "UP" / "DOWN" / "NEUTRAL"
    
    # Confidence
    overall_confidence: float  # 0-100
    signal_quality: SignalQuality
    
    # Risk Assessment
    risk_level: str  # "LOW" / "MEDIUM" / "HIGH"
    trap_probability: float  # %
    expected_move: Dict[str, float]  # {"min": %, "max": %}
    
    # Entry Points
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    
    # Additional
    invalidation_zone: Dict[str, float]  # {"above": price, "below": price}
    best_timeframe: str  # Recommended trading timeframe
    tradeable: bool
    reasoning: str
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "signal": self.predicted_direction,
            "probability_up": round(self.direction_probability_up, 2),
            "probability_down": round(self.direction_probability_down, 2),
            "confidence": round(self.overall_confidence, 2),
            "quality": self.signal_quality.value,
            "risk_level": self.risk_level,
            "trap_probability": round(self.trap_probability, 2),
            "expected_move_min": round(self.expected_move["min"], 2),
            "expected_move_max": round(self.expected_move["max"], 2),
            "entry": round(self.entry_price, 2),
            "stop_loss": round(self.stop_loss, 2),
            "tp1": round(self.take_profit_1, 2),
            "tp2": round(self.take_profit_2, 2),
            "tp3": round(self.take_profit_3, 2),
            "invalidation_above": round(self.invalidation_zone["above"], 2),
            "invalidation_below": round(self.invalidation_zone["below"], 2),
            "best_timeframe": self.best_timeframe,
            "tradeable": self.tradeable,
            "reasoning": self.reasoning
        }

# ==================== SIGNAL FUSION ENGINE ====================

class SignalFusionEngine:
    """Fuse all signals into final decision"""
    
    def __init__(self):
        self.min_confidence_threshold = 55  # Minimum to generate signal
    
    def fuse_signals(self,
                     symbol: str,
                     ensemble_signal: str,  # "BUY"/"SELL"/"NEUTRAL"
                     ensemble_confidence: float,
                     psychology_level: str,  # "EXTREME_FEAR", etc.
                     fear_score: float,
                     greed_score: float,
                     trap_probability: float,
                     entry_price: float,
                     stop_loss: float,
                     volatility_pct: float,
                     atr: float,
                     institutional_flow_strength: float) -> FinalTradingSignal:
        """Fuse all signals into final trading signal"""
        
        # ========== CALCULATE DIRECTION PROBABILITY ==========
        
        # Base probability from ensemble (0-100)
        ensemble_prob = ensemble_confidence * 100
        
        # Psychology adjustment
        if psychology_level in ["EXTREME_GREED", "GREED"]:
            psychology_bonus = 15  # Greed = upward bias
        elif psychology_level in ["EXTREME_FEAR", "FEAR"]:
            psychology_bonus = -15  # Fear = downward bias
        else:
            psychology_bonus = 0
        
        # Institutional flow adjustment
        if ensemble_signal == "BUY":
            flow_bonus = institutional_flow_strength * 10
        elif ensemble_signal == "SELL":
            flow_bonus = -institutional_flow_strength * 10
        else:
            flow_bonus = 0
        
        # Calculate final probabilities
        if ensemble_signal == "BUY" or ensemble_signal == "STRONG_BUY":
            up_prob = ensemble_prob + psychology_bonus + flow_bonus
            down_prob = 100 - up_prob
            predicted_direction = "UP"
        elif ensemble_signal == "SELL" or ensemble_signal == "STRONG_SELL":
            down_prob = ensemble_prob + abs(psychology_bonus) + abs(flow_bonus)
            up_prob = 100 - down_prob
            predicted_direction = "DOWN"
        else:
            up_prob = 50
            down_prob = 50
            predicted_direction = "NEUTRAL"
        
        # Clamp to 0-100
        up_prob = np.clip(up_prob, 0, 100)
        down_prob = np.clip(down_prob, 0, 100)
        
        # ========== CALCULATE CONFIDENCE ==========
        
        # Trap probability reduces confidence
        trap_penalty = (trap_probability / 100.0) * 30  # Max 30% penalty
        overall_confidence = max(self.min_confidence_threshold, ensemble_prob - trap_penalty)
        
        # ========== SIGNAL QUALITY ==========
        
        if overall_confidence >= 90:
            signal_quality = SignalQuality.EXCELLENT
        elif overall_confidence >= 70:
            signal_quality = SignalQuality.GOOD
        elif overall_confidence >= 50:
            signal_quality = SignalQuality.FAIR
        else:
            signal_quality = SignalQuality.POOR
        
        # ========== RISK LEVEL ==========
        
        if trap_probability > 70:
            risk_level = "HIGH"
        elif volatility_pct > 1.5:
            risk_level = "HIGH"
        elif volatility_pct > 0.8:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # ========== EXPECTED MOVE ==========
        
        # Based on ATR and IV
        expected_min = (atr / entry_price) * 100 * 0.8  # Conservative
        expected_max = (atr / entry_price) * 100 * 1.5  # Optimistic
        
        # ========== TAKE PROFITS ==========
        
        if predicted_direction == "UP":
            tp1 = entry_price + (atr * 1.0)
            tp2 = entry_price + (atr * 2.0)
            tp3 = entry_price + (atr * 3.0)
        elif predicted_direction == "DOWN":
            tp1 = entry_price - (atr * 1.0)
            tp2 = entry_price - (atr * 2.0)
            tp3 = entry_price - (atr * 3.0)
        else:
            tp1 = entry_price + atr
            tp2 = entry_price + (atr * 1.5)
            tp3 = entry_price + (atr * 2.0)
        
        # ========== INVALIDATION ZONES ==========
        
        invalidation_zone = {
            "above": entry_price + (atr * 2),
            "below": entry_price - (atr * 2)
        }
        
        # ========== TRADEABLE ==========
        
        tradeable = (
            overall_confidence >= self.min_confidence_threshold and
            predicted_direction != "NEUTRAL" and
            trap_probability <= 75
        )
        
        # ========== REASONING ==========
        
        reasoning = self._generate_detailed_reasoning(
            ensemble_signal,
            overall_confidence,
            psychology_level,
            trap_probability,
            institutional_flow_strength
        )
        
        # ========== BEST TIMEFRAME ==========
        
        if overall_confidence >= 85:
            best_tf = "15m - 1h"
        elif overall_confidence >= 70:
            best_tf = "5m - 15m"
        else:
            best_tf = "1h - 4h"
        
        return FinalTradingSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            direction_probability_up=up_prob,
            direction_probability_down=down_prob,
            predicted_direction=predicted_direction,
            overall_confidence=overall_confidence,
            signal_quality=signal_quality,
            risk_level=risk_level,
            trap_probability=trap_probability,
            expected_move={"min": expected_min, "max": expected_max},
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            invalidation_zone=invalidation_zone,
            best_timeframe=best_tf,
            tradeable=tradeable,
            reasoning=reasoning
        )
    
    @staticmethod
    def _generate_detailed_reasoning(ensemble_signal: str, confidence: float, psychology: str, trap_prob: float, flow_strength: float) -> str:
        """Generate detailed reasoning for signal"""
        
        parts = []
        
        # Ensemble component
        parts.append(f"Ensemble: {ensemble_signal} ({confidence:.0f}%)")
        
        # Psychology component
        if psychology in ["EXTREME_FEAR", "EXTREME_GREED"]:
            parts.append(f"⚠️ {psychology} - Extreme market condition")
        else:
            parts.append(f"Psychology: {psychology}")
        
        # Trap component
        if trap_prob > 70:
            parts.append(f"🚨 HIGH TRAP RISK ({trap_prob:.0f}%) - Use tight stops")
        elif trap_prob > 50:
            parts.append(f"⚠️ Moderate trap risk ({trap_prob:.0f}%)")
        
        # Flow component
        if flow_strength > 0.7:
            parts.append(f"✅ Strong institutional alignment")
        elif flow_strength < 0.3:
            parts.append(f"❌ Weak institutional support")
        
        return " | ".join(parts)

print("✅ PHASE 5: SIGNAL FUSION ENGINE - READY")
