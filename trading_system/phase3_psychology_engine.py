"""
🧠 INSTITUTIONAL AI TRADING SYSTEM - PHASE 3
PSYCHOLOGY ENGINE (Behavioral Analysis & Market Sentiment)

Multi-timeframe psychology + fear/greed scoring
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
from enum import Enum
import numpy as np

# ==================== PSYCHOLOGY ENUMS ====================

class PsychologyLevel(Enum):
    """Market psychology levels"""
    EXTREME_FEAR = 1
    FEAR = 2
    NEUTRAL = 3
    GREED = 4
    EXTREME_GREED = 5

class ParticipantType(Enum):
    """Market participant types"""
    RETAIL = "retail"  # 1m-5m
    SMART_MONEY = "smart_money"  # 15m-1h
    INSTITUTIONAL = "institutional"  # 4h-1d

# ==================== PSYCHOLOGY METRICS ====================

@dataclass
class FearScore:
    """Fear index components"""
    volatility_spike: float  # 0-100
    red_candle_intensity: float  # 0-100
    panic_selling_pressure: float  # 0-100
    liquidation_cascade: float  # 0-100
    overall_fear: float  # 0-100
    
    def to_dict(self):
        return {
            "volatility_spike": round(self.volatility_spike, 2),
            "red_candle_intensity": round(self.red_candle_intensity, 2),
            "panic_pressure": round(self.panic_selling_pressure, 2),
            "liquidations": round(self.liquidation_cascade, 2),
            "overall_fear": round(self.overall_fear, 2)
        }

@dataclass
class GreedScore:
    """Greed index components"""
    breakout_momentum: float  # 0-100
    fomo_buying_pressure: float  # 0-100
    trend_acceleration: float  # 0-100
    momentum_velocity: float  # 0-100
    overall_greed: float  # 0-100
    
    def to_dict(self):
        return {
            "breakout_momentum": round(self.breakout_momentum, 2),
            "fomo_pressure": round(self.fomo_buying_pressure, 2),
            "trend_acceleration": round(self.trend_acceleration, 2),
            "momentum_velocity": round(self.momentum_velocity, 2),
            "overall_greed": round(self.overall_greed, 2)
        }

@dataclass
class TrapSignal:
    """Trap/False breakout detection"""
    fake_breakout_probability: float  # 0-100
    wick_rejection_strength: float  # 0-100
    oi_mismatch_alert: bool
    liquidity_sweep_imminent: float  # 0-100
    invalidation_probability: float  # 0-100
    
    def to_dict(self):
        return {
            "fake_breakout_prob": round(self.fake_breakout_probability, 2),
            "wick_rejection": round(self.wick_rejection_strength, 2),
            "oi_mismatch": self.oi_mismatch_alert,
            "liquidity_sweep": round(self.liquidity_sweep_imminent, 2),
            "invalidation_prob": round(self.invalidation_probability, 2)
        }

@dataclass
class InstitutionalFlow:
    """Institutional/Smart money flow detection"""
    trend_consistency: float  # 0-100
    volume_confirmation: float  # 0-100
    oi_alignment: float  # 0-100
    flow_strength: float  # 0-100
    flow_confidence: float  # 0-100
    
    def to_dict(self):
        return {
            "trend_consistency": round(self.trend_consistency, 2),
            "volume_confirmation": round(self.volume_confirmation, 2),
            "oi_alignment": round(self.oi_alignment, 2),
            "flow_strength": round(self.flow_strength, 2),
            "confidence": round(self.flow_confidence, 2)
        }

@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe psychology breakdown"""
    retail_behavior: Dict[str, float]  # 1m-5m analysis
    smart_money_behavior: Dict[str, float]  # 15m-1h analysis
    institutional_trend: Dict[str, float]  # 4h-1d analysis
    alignment: float  # 0-100: how aligned are timeframes
    
    def to_dict(self):
        return {
            "retail": self.retail_behavior,
            "smart_money": self.smart_money_behavior,
            "institutional": self.institutional_trend,
            "alignment": round(self.alignment, 2)
        }

# ==================== PSYCHOLOGY ENGINE ====================

class PsychologyEngine:
    """Market psychology analysis system"""
    
    def __init__(self):
        self.fear_threshold = 70  # Fear triggers above 70
        self.greed_threshold = 70  # Greed triggers above 70
        self.trap_threshold = 65  # Trap signals above 65
    
    def calculate_fear_score(self, volatility_pct: float, red_candle_count: int, volume_spike: float, liquidation_indicator: float) -> FearScore:
        """Calculate fear index"""
        
        # Volatility spike component (0-100)
        vol_spike = min(100, (volatility_pct / 2.0) * 100)
        
        # Red candle intensity (0-100)
        red_intensity = min(100, red_candle_count * 20)
        
        # Panic selling pressure (0-100)
        panic_pressure = min(100, volume_spike * 50)
        
        # Liquidation cascade (0-100)
        liquidation = min(100, liquidation_indicator * 100)
        
        # Overall fear (weighted average)
        overall = (vol_spike * 0.3 + red_intensity * 0.25 + panic_pressure * 0.25 + liquidation * 0.2)
        
        return FearScore(
            volatility_spike=vol_spike,
            red_candle_intensity=red_intensity,
            panic_selling_pressure=panic_pressure,
            liquidation_cascade=liquidation,
            overall_fear=overall
        )
    
    def calculate_greed_score(self, breakout_strength: float, green_candle_count: int, momentum: float, velocity: float) -> GreedScore:
        """Calculate greed index"""
        
        # Breakout momentum (0-100)
        breakout = min(100, breakout_strength * 100)
        
        # FOMO buying pressure (0-100)
        fomo = min(100, green_candle_count * 20)
        
        # Trend acceleration (0-100)
        accel = min(100, momentum * 100)
        
        # Momentum velocity (0-100)
        vel = min(100, velocity * 100)
        
        # Overall greed (weighted average)
        overall = (breakout * 0.3 + fomo * 0.25 + accel * 0.25 + vel * 0.2)
        
        return GreedScore(
            breakout_momentum=breakout,
            fomo_buying_pressure=fomo,
            trend_acceleration=accel,
            momentum_velocity=vel,
            overall_greed=overall
        )
    
    def detect_trap_signals(self, wick_strength: float, oi_mismatch: bool, liquidity_zone_proximity: float, breakout_failure_prob: float) -> TrapSignal:
        """Detect fake breakouts and traps"""
        
        # Fake breakout probability (0-100)
        fake_breakout = breakout_failure_prob * 100
        
        # Wick rejection strength (0-100)
        wick_rejection = min(100, wick_strength * 100)
        
        # Liquidity sweep proximity (0-100)
        liquidity_sweep = min(100, (1.0 - liquidity_zone_proximity) * 100)
        
        # Invalidation probability (0-100)
        invalidation = (fake_breakout + wick_rejection + liquidity_sweep) / 3.0
        
        return TrapSignal(
            fake_breakout_probability=fake_breakout,
            wick_rejection_strength=wick_rejection,
            oi_mismatch_alert=oi_mismatch,
            liquidity_sweep_imminent=liquidity_sweep,
            invalidation_probability=invalidation
        )
    
    def analyze_institutional_flow(self, trend_consistency: float, volume_confirmation: float, oi_alignment: float) -> InstitutionalFlow:
        """Analyze institutional/smart money flow"""
        
        # Trend consistency (0-100)
        consistency = trend_consistency * 100
        
        # Volume confirmation (0-100)
        vol_conf = volume_confirmation * 100
        
        # OI alignment (0-100)
        oi_align = oi_alignment * 100
        
        # Flow strength (average)
        flow_strength = (consistency + vol_conf + oi_align) / 3.0
        
        # Confidence
        confidence = min(100, flow_strength * 1.2)
        
        return InstitutionalFlow(
            trend_consistency=consistency,
            volume_confirmation=vol_conf,
            oi_alignment=oi_align,
            flow_strength=flow_strength,
            flow_confidence=confidence
        )
    
    def multi_timeframe_psychology(self, retail_metrics: Dict, smart_money_metrics: Dict, institutional_metrics: Dict) -> MultiTimeframeAnalysis:
        """Analyze psychology across timeframes"""
        
        # Calculate alignment
        retail_direction = 1 if retail_metrics.get("trend", 0) > 0 else -1
        smart_direction = 1 if smart_money_metrics.get("trend", 0) > 0 else -1
        inst_direction = 1 if institutional_metrics.get("trend", 0) > 0 else -1
        
        alignment_score = 0
        if retail_direction == smart_direction == inst_direction:
            alignment_score = 100  # All aligned
        elif retail_direction == smart_direction or smart_direction == inst_direction:
            alignment_score = 60  # Partially aligned
        else:
            alignment_score = 20  # Diverged
        
        return MultiTimeframeAnalysis(
            retail_behavior=retail_metrics,
            smart_money_behavior=smart_money_metrics,
            institutional_trend=institutional_metrics,
            alignment=alignment_score
        )
    
    def get_psychology_level(self, fear_score: float, greed_score: float) -> PsychologyLevel:
        """Determine overall market psychology level"""
        
        net_score = greed_score - fear_score
        
        if net_score > 40:
            return PsychologyLevel.EXTREME_GREED
        elif net_score > 20:
            return PsychologyLevel.GREED
        elif net_score > -20:
            return PsychologyLevel.NEUTRAL
        elif net_score > -40:
            return PsychologyLevel.FEAR
        else:
            return PsychologyLevel.EXTREME_FEAR
    
    def generate_psychology_report(self, fear: FearScore, greed: GreedScore, trap: TrapSignal, flow: InstitutionalFlow) -> Dict:
        """Generate comprehensive psychology report"""
        
        psychology_level = self.get_psychology_level(fear.overall_fear, greed.overall_greed)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_psychology": psychology_level.name,
            "fear_score": fear.to_dict(),
            "greed_score": greed.to_dict(),
            "trap_detection": trap.to_dict(),
            "institutional_flow": flow.to_dict(),
            "recommendation": self._generate_recommendation(psychology_level, trap)
        }
    
    @staticmethod
    def _generate_recommendation(psychology: PsychologyLevel, trap: TrapSignal) -> str:
        """Generate trading recommendation based on psychology"""
        
        if trap.invalidation_probability > 70:
            return "⚠️ HIGH TRAP PROBABILITY - AVOID BREAKOUT TRADES"
        
        if psychology == PsychologyLevel.EXTREME_FEAR:
            return "🔴 EXTREME FEAR - Potential reversal area, wait for confirmation"
        elif psychology == PsychologyLevel.FEAR:
            return "🟠 FEAR ZONE - Consider mean reversion setups"
        elif psychology == PsychologyLevel.NEUTRAL:
            return "🟡 NEUTRAL - Wait for clear direction signal"
        elif psychology == PsychologyLevel.GREED:
            return "🟢 GREED ZONE - Trend following strategies viable"
        else:  # EXTREME_GREED
            return "🔴 EXTREME GREED - High risk, consider profit taking"

print("✅ PHASE 3: PSYCHOLOGY ENGINE - READY")
