"""
🧠 INSTITUTIONAL AI TRADING SYSTEM - PHASE 4
STRATEGY ENGINE (Multi-Model Ensemble System)

Multiple strategies voting on final trade signal
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import numpy as np

# ==================== STRATEGY ENUMS ====================

class TradeDirection(Enum):
    LONG = 1
    SHORT = -1
    NEUTRAL = 0

class StrategySignal(Enum):
    STRONG_BUY = 2
    BUY = 1
    NEUTRAL = 0
    SELL = -1
    STRONG_SELL = -2

# ==================== STRATEGY OUTPUTS ====================

@dataclass
class StrategyOutput:
    """Single strategy output"""
    strategy_name: str
    signal: StrategySignal
    confidence: float  # 0-1
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    reasoning: str
    
    def to_dict(self):
        return {
            "strategy": self.strategy_name,
            "signal": self.signal.name,
            "confidence": round(self.confidence, 2),
            "entry": round(self.entry_price, 2),
            "sl": round(self.stop_loss, 2),
            "tp": round(self.take_profit, 2),
            "rrr": round(self.risk_reward_ratio, 2),
            "reasoning": self.reasoning
        }

# ==================== INDIVIDUAL STRATEGIES ====================

class TrendFollowingStrategy:
    """Strategy 1: Trend Following with EMA"""
    
    @staticmethod
    def analyze(closes: List[float], atr: float, current_price: float) -> StrategyOutput:
        """Trend following logic"""
        
        ema_5 = np.mean(closes[-5:])
        ema_20 = np.mean(closes[-20:])
        ema_50 = np.mean(closes[-50:])
        
        # Trend analysis
        if ema_5 > ema_20 > ema_50:
            signal = StrategySignal.STRONG_BUY
            confidence = 0.85
            direction = TradeDirection.LONG
            entry = current_price
            sl = current_price - (2 * atr)
            tp = current_price + (4 * atr)
            reasoning = "Strong uptrend with all EMAs aligned"
        
        elif ema_5 < ema_20 < ema_50:
            signal = StrategySignal.STRONG_SELL
            confidence = 0.85
            direction = TradeDirection.SHORT
            entry = current_price
            sl = current_price + (2 * atr)
            tp = current_price - (4 * atr)
            reasoning = "Strong downtrend with all EMAs aligned"
        
        elif ema_5 > ema_20:
            signal = StrategySignal.BUY
            confidence = 0.60
            direction = TradeDirection.LONG
            entry = current_price
            sl = current_price - (2 * atr)
            tp = current_price + (3 * atr)
            reasoning = "Short-term uptrend detected"
        
        elif ema_5 < ema_20:
            signal = StrategySignal.SELL
            confidence = 0.60
            direction = TradeDirection.SHORT
            entry = current_price
            sl = current_price + (2 * atr)
            tp = current_price - (3 * atr)
            reasoning = "Short-term downtrend detected"
        
        else:
            signal = StrategySignal.NEUTRAL
            confidence = 0.40
            direction = TradeDirection.NEUTRAL
            entry = current_price
            sl = current_price - atr
            tp = current_price + atr
            reasoning = "No clear trend"
        
        rrr = abs(tp - entry) / (abs(entry - sl) + 0.0001)
        
        return StrategyOutput(
            strategy_name="Trend Following (EMA)",
            signal=signal,
            confidence=confidence,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            risk_reward_ratio=rrr,
            reasoning=reasoning
        )

class MeanReversionStrategy:
    """Strategy 2: Mean Reversion"""
    
    @staticmethod
    def analyze(closes: List[float], rsi: float, atr: float, current_price: float) -> StrategyOutput:
        """Mean reversion logic"""
        
        # Overbought/Oversold
        if rsi > 70:
            signal = StrategySignal.SELL
            confidence = 0.65
            direction = TradeDirection.SHORT
            entry = current_price
            sl = current_price + (2 * atr)
            tp = current_price - (3 * atr)
            reasoning = f"RSI Overbought at {rsi:.1f} - Mean reversion sell"
        
        elif rsi < 30:
            signal = StrategySignal.BUY
            confidence = 0.65
            direction = TradeDirection.LONG
            entry = current_price
            sl = current_price - (2 * atr)
            tp = current_price + (3 * atr)
            reasoning = f"RSI Oversold at {rsi:.1f} - Mean reversion buy"
        
        else:
            signal = StrategySignal.NEUTRAL
            confidence = 0.30
            direction = TradeDirection.NEUTRAL
            entry = current_price
            sl = current_price - atr
            tp = current_price + atr
            reasoning = "RSI in neutral zone"
        
        rrr = abs(tp - entry) / (abs(entry - sl) + 0.0001)
        
        return StrategyOutput(
            strategy_name="Mean Reversion (RSI)",
            signal=signal,
            confidence=confidence,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            risk_reward_ratio=rrr,
            reasoning=reasoning
        )

class OptionsFlowStrategy:
    """Strategy 3: Options Flow Analysis"""
    
    @staticmethod
    def analyze(pcr: float, oi_buildup: str, iv_rank: float, atr: float, current_price: float) -> StrategyOutput:
        """Options flow logic"""
        
        # OI buildup direction
        if oi_buildup == "calls" and pcr < 0.8:
            signal = StrategySignal.STRONG_BUY
            confidence = 0.70
            reasoning = "Call OI buildup with low PCR - bullish"
            entry = current_price
            sl = current_price - (1.5 * atr)
            tp = current_price + (4 * atr)
        
        elif oi_buildup == "puts" and pcr > 1.2:
            signal = StrategySignal.STRONG_SELL
            confidence = 0.70
            reasoning = "Put OI buildup with high PCR - bearish"
            entry = current_price
            sl = current_price + (1.5 * atr)
            tp = current_price - (4 * atr)
        
        else:
            signal = StrategySignal.NEUTRAL
            confidence = 0.40
            reasoning = "Mixed options flow"
            entry = current_price
            sl = current_price - atr
            tp = current_price + atr
        
        rrr = abs(tp - entry) / (abs(entry - sl) + 0.0001)
        
        return StrategyOutput(
            strategy_name="Options Flow",
            signal=signal,
            confidence=confidence,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            risk_reward_ratio=rrr,
            reasoning=reasoning
        )

class TrapDetectionStrategy:
    """Strategy 4: Trap Detection (Avoidance)"""
    
    @staticmethod
    def analyze(trap_probability: float, wick_strength: float, breakout_fail_prob: float, atr: float, current_price: float) -> StrategyOutput:
        """Trap avoidance logic"""
        
        trap_score = (trap_probability + (wick_strength * 100) + (breakout_fail_prob * 100)) / 3.0
        
        if trap_score > 70:
            signal = StrategySignal.NEUTRAL
            confidence = 0.90
            reasoning = f"🚨 HIGH TRAP PROBABILITY ({trap_score:.0f}%) - AVOID BREAKOUT"
            direction = TradeDirection.NEUTRAL
        
        elif trap_score > 50:
            signal = StrategySignal.NEUTRAL
            confidence = 0.70
            reasoning = f"⚠️ MODERATE TRAP RISK - Use tight stops"
            direction = TradeDirection.NEUTRAL
        
        else:
            signal = StrategySignal.BUY if breakout_fail_prob < 0.3 else StrategySignal.SELL
            confidence = 0.55
            reasoning = "Low trap probability - Breakout viable"
            direction = TradeDirection.LONG if breakout_fail_prob < 0.3 else TradeDirection.SHORT
        
        entry = current_price
        sl = current_price - (1.5 * atr)
        tp = current_price + (2 * atr)
        rrr = abs(tp - entry) / (abs(entry - sl) + 0.0001)
        
        return StrategyOutput(
            strategy_name="Trap Detection",
            signal=signal,
            confidence=confidence,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            risk_reward_ratio=rrr,
            reasoning=reasoning
        )

# ==================== ENSEMBLE VOTING SYSTEM ====================

class StrategyEnsemble:
    """Combine multiple strategies via voting"""
    
    def __init__(self):
        self.strategies: List[StrategyOutput] = []
    
    def add_strategy_output(self, output: StrategyOutput) -> None:
        """Add strategy result to ensemble"""
        self.strategies.append(output)
    
    def get_ensemble_signal(self) -> Tuple[StrategySignal, float, Dict]:
        """Calculate ensemble signal via weighted voting"""
        
        if not self.strategies:
            return StrategySignal.NEUTRAL, 0.0, {}
        
        # Weighted voting
        buy_votes = 0
        sell_votes = 0
        neutral_votes = 0
        total_confidence = 0
        
        for strategy in self.strategies:
            weight = strategy.confidence
            
            if strategy.signal == StrategySignal.STRONG_BUY:
                buy_votes += 2 * weight
            elif strategy.signal == StrategySignal.BUY:
                buy_votes += weight
            elif strategy.signal == StrategySignal.SELL:
                sell_votes += weight
            elif strategy.signal == StrategySignal.STRONG_SELL:
                sell_votes += 2 * weight
            else:
                neutral_votes += weight
            
            total_confidence += weight
        
        # Determine final signal
        if buy_votes > sell_votes and buy_votes > 0:
            final_signal = StrategySignal.BUY if buy_votes < 3 else StrategySignal.STRONG_BUY
            confidence = buy_votes / total_confidence if total_confidence > 0 else 0
        elif sell_votes > buy_votes and sell_votes > 0:
            final_signal = StrategySignal.SELL if sell_votes < 3 else StrategySignal.STRONG_SELL
            confidence = sell_votes / total_confidence if total_confidence > 0 else 0
        else:
            final_signal = StrategySignal.NEUTRAL
            confidence = neutral_votes / total_confidence if total_confidence > 0 else 0.5
        
        details = {
            "strategies_analyzed": len(self.strategies),
            "buy_votes": round(buy_votes, 2),
            "sell_votes": round(sell_votes, 2),
            "consensus_strength": round(max(buy_votes, sell_votes, neutral_votes) / total_confidence, 2) if total_confidence > 0 else 0
        }
        
        return final_signal, confidence, details
    
    def generate_ensemble_report(self) -> Dict:
        """Generate full ensemble analysis report"""
        
        final_signal, confidence, details = self.get_ensemble_signal()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "final_signal": final_signal.name,
            "confidence": round(confidence, 2),
            "ensemble_details": details,
            "strategy_breakdown": [s.to_dict() for s in self.strategies],
            "recommendation": self._generate_recommendation(final_signal, confidence)
        }
    
    @staticmethod
    def _generate_recommendation(signal: StrategySignal, confidence: float) -> str:
        """Generate final trading recommendation"""
        
        if confidence < 0.5:
            return "❌ INSUFFICIENT CONSENSUS - Wait for clearer signal"
        
        if signal == StrategySignal.STRONG_BUY:
            return f"✅ STRONG BUY (Confidence: {confidence:.1%}) - High probability trade"
        elif signal == StrategySignal.BUY:
            return f"🟢 BUY (Confidence: {confidence:.1%}) - Moderate bias up"
        elif signal == StrategySignal.SELL:
            return f"🔴 SELL (Confidence: {confidence:.1%}) - Moderate bias down"
        elif signal == StrategySignal.STRONG_SELL:
            return f"❌ STRONG SELL (Confidence: {confidence:.1%}) - High probability trade"
        else:
            return f"🟡 NEUTRAL (Confidence: {confidence:.1%}) - Wait for confirmation"

from datetime import datetime
print("✅ PHASE 4: STRATEGY ENGINE - READY")
