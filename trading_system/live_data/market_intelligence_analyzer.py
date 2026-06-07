"""
📋 ADVANCED MARKET INTELLIGENCE ANALYZER
Analyzes: FII/DII + VIX + OI + PCR + Volume + LTP
Outputs: Bullish/Bearish signal with point targets
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ANALYSIS ENUMS ====================

class MarketSentiment(Enum):
    EXTREMELY_BULLISH = "EXTREMELY_BULLISH"      # +200 to +500 points
    STRONGLY_BULLISH = "STRONGLY_BULLISH"        # +100 to +200 points
    MODERATELY_BULLISH = "MODERATELY_BULLISH"    # +50 to +100 points
    SLIGHTLY_BULLISH = "SLIGHTLY_BULLISH"        # +20 to +50 points
    NEUTRAL = "NEUTRAL"                          # -20 to +20 points
    SLIGHTLY_BEARISH = "SLIGHTLY_BEARISH"        # -50 to -20 points
    MODERATELY_BEARISH = "MODERATELY_BEARISH"    # -100 to -50 points
    STRONGLY_BEARISH = "STRONGLY_BEARISH"        # -200 to -100 points
    EXTREMELY_BEARISH = "EXTREMELY_BEARISH"      # -500 to -200 points

from enum import Enum

# ==================== ANALYSIS RESULTS ====================

@dataclass
class MarketIntelligenceReport:
    """
    Complete market analysis report
    """
    timestamp: datetime
    symbol: str
    ltp: float
    
    # Overall Sentiment
    sentiment: str  # BULLISH / BEARISH / NEUTRAL
    confidence: float  # 0-100
    
    # Point Targets
    expected_move_up: float  # Points
    expected_move_down: float  # Points
    target_resistance: float  # Price target
    target_support: float  # Price support
    
    # Component Analysis
    fii_signal: float  # -100 to +100
    vix_signal: float
    oi_signal: float
    pcr_signal: float
    volume_signal: float
    price_signal: float
    
    # Detailed Reasoning
    key_factors: List[str]
    warnings: List[str]
    recommendation: str
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "ltp": round(self.ltp, 2),
            "sentiment": self.sentiment,
            "confidence": round(self.confidence, 2),
            "targets": {
                "up_points": round(self.expected_move_up, 2),
                "down_points": round(self.expected_move_down, 2),
                "resistance": round(self.target_resistance, 2),
                "support": round(self.target_support, 2)
            },
            "component_signals": {
                "fii": round(self.fii_signal, 2),
                "vix": round(self.vix_signal, 2),
                "oi": round(self.oi_signal, 2),
                "pcr": round(self.pcr_signal, 2),
                "volume": round(self.volume_signal, 2),
                "price": round(self.price_signal, 2)
            },
            "key_factors": self.key_factors,
            "warnings": self.warnings,
            "recommendation": self.recommendation
        }

# ==================== MARKET INTELLIGENCE ENGINE ====================

class MarketIntelligenceAnalyzer:
    """
    Advanced market analysis combining all indicators
    """
    
    def __init__(self):
        self.fii_weight = 0.25
        self.vix_weight = 0.15
        self.oi_weight = 0.20
        self.pcr_weight = 0.20
        self.volume_weight = 0.10
        self.price_weight = 0.10
    
    def analyze_complete_market(self, snapshot) -> MarketIntelligenceReport:
        """
        Analyze all indicators together
        
        Args:
            snapshot: MarketSnapshot object from live_market_fetcher
        
        Returns:
            MarketIntelligenceReport with complete analysis
        """
        
        # Analyze each component
        fii_signal = self._analyze_fii_dii(snapshot)
        vix_signal = self._analyze_vix(snapshot)
        oi_signal = self._analyze_oi(snapshot)
        pcr_signal = self._analyze_pcr(snapshot)
        volume_signal = self._analyze_volume(snapshot)
        price_signal = self._analyze_price(snapshot)
        
        # Calculate composite score
        composite_score = (
            fii_signal * self.fii_weight +
            vix_signal * self.vix_weight +
            oi_signal * self.oi_weight +
            pcr_signal * self.pcr_weight +
            volume_signal * self.volume_weight +
            price_signal * self.price_weight
        )
        
        # Determine sentiment and targets
        sentiment, confidence, targets = self._determine_sentiment_and_targets(
            composite_score, snapshot
        )
        
        # Generate key factors
        key_factors = self._generate_key_factors(snapshot, fii_signal, vix_signal, oi_signal, pcr_signal)
        
        # Generate warnings
        warnings = self._generate_warnings(snapshot, vix_signal, pcr_signal)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(sentiment, confidence, snapshot)
        
        report = MarketIntelligenceReport(
            timestamp=snapshot.timestamp,
            symbol=snapshot.symbol,
            ltp=snapshot.ltp,
            sentiment=sentiment,
            confidence=confidence,
            expected_move_up=targets["up"],
            expected_move_down=targets["down"],
            target_resistance=targets["resistance"],
            target_support=targets["support"],
            fii_signal=fii_signal,
            vix_signal=vix_signal,
            oi_signal=oi_signal,
            pcr_signal=pcr_signal,
            volume_signal=volume_signal,
            price_signal=price_signal,
            key_factors=key_factors,
            warnings=warnings,
            recommendation=recommendation
        )
        
        logger.info(f"📋 {sentiment} | Confidence: {confidence:.0f}% | Up: +{targets['up']:.0f}pts | Down: -{targets['down']:.0f}pts")
        
        return report
    
    # ==================== COMPONENT ANALYSIS ====================
    
    def _analyze_fii_dii(self, snapshot) -> float:
        """
        Analyze FII/DII flow
        Returns: -100 to +100
        
        Logic:
        - FII buying = bullish
        - FII selling = bearish
        - Strong flows have more weight
        """
        fii_net = snapshot.fii_flow.get("net", 0)
        
        # Normalize FII flow (-1000 to +1000 becomes -100 to +100)
        if fii_net > 500:
            signal = 100  # Extreme buying
        elif fii_net > 200:
            signal = 70   # Strong buying
        elif fii_net > 50:
            signal = 40   # Moderate buying
        elif fii_net > 0:
            signal = 15   # Slight buying
        elif fii_net > -50:
            signal = -15  # Slight selling
        elif fii_net > -200:
            signal = -40  # Moderate selling
        elif fii_net > -500:
            signal = -70  # Strong selling
        else:
            signal = -100  # Extreme selling
        
        logger.info(f"📊 FII Flow: {fii_net:+.2f}M USD | Signal: {signal:+.0f}")
        return signal
    
    def _analyze_vix(self, snapshot) -> float:
        """
        Analyze VIX (Market Volatility/Fear Index)
        Returns: -100 to +100
        
        Logic:
        - VIX > 25 = High fear = Potential bottom
        - VIX < 15 = Complacency = Caution
        - Spike in VIX = Temporary panic
        """
        vix = snapshot.vix
        vix_change = snapshot.vix_change
        
        # VIX trend
        if vix > 30:  # Extreme fear
            signal = 80  # Bullish reversal setup
        elif vix > 25:
            signal = 60  # Strong fear
        elif vix > 20:
            signal = 30  # Elevated fear
        elif vix > 15:
            signal = 0   # Normal
        elif vix < 12:
            signal = -50  # Complacency risk
        else:
            signal = -20
        
        # Spike adjustment
        if vix_change > 2:  # VIX spiking
            signal += 20  # Adds bullish reversal potential
        
        logger.info(f"📊 VIX: {vix:.2f} ({vix_change:+.2f}) | Signal: {signal:+.0f}")
        return signal
    
    def _analyze_oi(self, snapshot) -> float:
        """
        Analyze Open Interest Changes
        Returns: -100 to +100
        
        Logic:
        - OI increasing + price up = Strength
        - OI increasing + price down = Distribution/Weakness
        - OI decreasing = Profit booking
        """
        oi_change_pct = snapshot.oi_change_percent
        price_change_pct = snapshot.change_percent
        
        # OI buildup
        if oi_change_pct > 5:  # Strong OI buildup
            if price_change_pct > 0:
                signal = 80  # Bullish: OI up + price up
            else:
                signal = -60  # Bearish: OI up + price down (distribution)
        elif oi_change_pct > 2:
            if price_change_pct > 0:
                signal = 50
            else:
                signal = -30
        elif oi_change_pct > 0:
            if price_change_pct > 0:
                signal = 20
            else:
                signal = -10
        else:  # OI decreasing
            if price_change_pct > 0:
                signal = -20  # Weak pullback
            else:
                signal = 20   # Profit booking (could be reversal)
        
        logger.info(f"📊 OI Change: {oi_change_pct:+.2f}% | Signal: {signal:+.0f}")
        return signal
    
    def _analyze_pcr(self, snapshot) -> float:
        """
        Analyze Put-Call Ratio
        Returns: -100 to +100
        
        Logic:
        - PCR > 1.2 = More puts than calls = Bearish
        - PCR < 0.8 = More calls than puts = Bullish
        - PCR = 1.0 = Neutral/Balanced
        """
        pcr = snapshot.pcr_ratio
        
        if pcr < 0.7:  # Strong call buildup
            signal = 85  # Extremely bullish
        elif pcr < 0.85:
            signal = 60  # Strongly bullish
        elif pcr < 1.0:
            signal = 30  # Moderately bullish
        elif pcr < 1.1:
            signal = 0   # Neutral
        elif pcr < 1.3:
            signal = -30  # Moderately bearish
        elif pcr < 1.5:
            signal = -60  # Strongly bearish
        else:
            signal = -85  # Extremely bearish
        
        logger.info(f"📊 PCR: {pcr:.2f} | Signal: {signal:+.0f}")
        return signal
    
    def _analyze_volume(self, snapshot) -> float:
        """
        Analyze Volume Profile
        Returns: -100 to +100
        
        Logic:
        - High volume on up days = Strong buying
        - High volume on down days = Strong selling
        - Low volume = Weak conviction
        """
        volume_ratio = snapshot.volume_ratio
        price_change = snapshot.change_percent
        
        # Volume spike
        if volume_ratio > 2.0:  # 2x average volume
            if price_change > 0:
                signal = 75  # Strong buying
            else:
                signal = -75  # Strong selling
        elif volume_ratio > 1.5:
            if price_change > 0:
                signal = 50
            else:
                signal = -50
        elif volume_ratio > 1.2:
            if price_change > 0:
                signal = 25
            else:
                signal = -25
        else:  # Normal or low volume
            if price_change > 0:
                signal = 10
            else:
                signal = -10
        
        logger.info(f"📊 Volume Ratio: {volume_ratio:.2f}x | Signal: {signal:+.0f}")
        return signal
    
    def _analyze_price(self, snapshot) -> float:
        """
        Analyze Current Price Action
        Returns: -100 to +100
        
        Logic:
        - Large positive change = Momentum
        - Large negative change = Weakness
        """
        change_pct = snapshot.change_percent
        
        if change_pct > 2:
            signal = 60  # Strong uptrend
        elif change_pct > 1:
            signal = 35  # Moderate uptrend
        elif change_pct > 0.5:
            signal = 15  # Mild uptrend
        elif change_pct > 0:
            signal = 5   # Slight up
        elif change_pct > -0.5:
            signal = -5
        elif change_pct > -1:
            signal = -15
        elif change_pct > -2:
            signal = -35
        else:
            signal = -60  # Strong downtrend
        
        logger.info(f"📊 Price Change: {change_pct:+.2f}% | Signal: {signal:+.0f}")
        return signal
    
    # ==================== SENTIMENT DETERMINATION ====================
    
    def _determine_sentiment_and_targets(self, composite_score: float, snapshot) -> Tuple[str, float, Dict]:
        """
        Determine market sentiment and price targets based on composite score
        
        Returns:
            (sentiment, confidence, targets)
        """
        ltp = snapshot.ltp
        atr = 150  # Average True Range (example)
        
        # Sentiment based on score
        if composite_score > 60:
            sentiment = "🚀 EXTREMELY BULLISH"
            confidence = min(95, 60 + abs(composite_score) * 0.5)
            # Targets: large upside
            targets = {
                "up": atr * 3,
                "down": atr * 0.5,
                "resistance": ltp + (atr * 3),
                "support": ltp - (atr * 0.5)
            }
        elif composite_score > 40:
            sentiment = "😀 STRONGLY BULLISH"
            confidence = 60 + composite_score * 0.3
            targets = {
                "up": atr * 2.5,
                "down": atr * 0.8,
                "resistance": ltp + (atr * 2.5),
                "support": ltp - (atr * 0.8)
            }
        elif composite_score > 20:
            sentiment = "😊 MODERATELY BULLISH"
            confidence = 50 + composite_score * 0.4
            targets = {
                "up": atr * 1.5,
                "down": atr * 1.0,
                "resistance": ltp + (atr * 1.5),
                "support": ltp - (atr * 1.0)
            }
        elif composite_score > 0:
            sentiment = "😈 SLIGHTLY BULLISH"
            confidence = 50 + composite_score * 0.2
            targets = {
                "up": atr * 0.8,
                "down": atr * 0.8,
                "resistance": ltp + (atr * 0.8),
                "support": ltp - (atr * 0.8)
            }
        elif composite_score > -20:
            sentiment = "😐 NEUTRAL"
            confidence = 40
            targets = {
                "up": atr * 0.5,
                "down": atr * 0.5,
                "resistance": ltp + (atr * 0.5),
                "support": ltp - (atr * 0.5)
            }
        elif composite_score > -40:
            sentiment = "😩 SLIGHTLY BEARISH"
            confidence = 50 + abs(composite_score) * 0.2
            targets = {
                "up": atr * 0.8,
                "down": atr * 0.8,
                "resistance": ltp + (atr * 0.8),
                "support": ltp - (atr * 0.8)
            }
        elif composite_score > -60:
            sentiment = "😫 MODERATELY BEARISH"
            confidence = 50 + abs(composite_score) * 0.4
            targets = {
                "up": atr * 1.0,
                "down": atr * 1.5,
                "resistance": ltp + (atr * 1.0),
                "support": ltp - (atr * 1.5)
            }
        elif composite_score > -80:
            sentiment = "😓 STRONGLY BEARISH"
            confidence = 60 + abs(composite_score) * 0.3
            targets = {
                "up": atr * 0.8,
                "down": atr * 2.5,
                "resistance": ltp + (atr * 0.8),
                "support": ltp - (atr * 2.5)
            }
        else:
            sentiment = "🙀 EXTREMELY BEARISH"
            confidence = min(95, 60 + abs(composite_score) * 0.5)
            targets = {
                "up": atr * 0.5,
                "down": atr * 3,
                "resistance": ltp + (atr * 0.5),
                "support": ltp - (atr * 3)
            }
        
        return sentiment, confidence, targets
    
    def _generate_key_factors(self, snapshot, fii_sig, vix_sig, oi_sig, pcr_sig) -> List[str]:
        """
        Generate key bullish/bearish factors
        """
        factors = []
        
        if fii_sig > 50:
            factors.append("💪 FII in strong buying mode (+{:.0f}M USD)".format(snapshot.fii_flow.get("net", 0)))
        elif fii_sig < -50:
            factors.append("💫 FII in selling mode (-{:.0f}M USD)".format(abs(snapshot.fii_flow.get("net", 0))))
        
        if vix_sig > 50:
            factors.append("⚠️ High VIX ({:.2f}) - Market uncertainty".format(snapshot.vix))
        
        if oi_sig > 50:
            factors.append("📈 Strong OI buildup - New long positions".format())
        elif oi_sig < -50:
            factors.append("📉 OI distribution - Weak hands exiting".format())
        
        if pcr_sig > 50:
            factors.append("🔴 High PCR ({:.2f}) - Put protection buying".format(snapshot.pcr_ratio))
        elif pcr_sig < -50:
            factors.append("🔵 Low PCR ({:.2f}) - Call buying aggression".format(snapshot.pcr_ratio))
        
        if snapshot.volume_ratio > 1.5:
            factors.append("📊 High volume ({:.2f}x average) - Strong conviction".format(snapshot.volume_ratio))
        
        return factors
    
    def _generate_warnings(self, snapshot, vix_sig, pcr_sig) -> List[str]:
        """
        Generate warning signals
        """
        warnings = []
        
        if snapshot.vix > 25:
            warnings.append("🚨 High volatility - Use smaller positions")
        
        if abs(snapshot.pcr_ratio - 1.0) > 0.3:
            warnings.append("⚠️ Extreme PCR reading - Possible exhaustion")
        
        if snapshot.volume < snapshot.volume_avg_20 * 0.5:
            warnings.append("😳 Low volume - Weak move, be cautious")
        
        if snapshot.bid_ask_spread > 5:
            warnings.append("📄 Wide bid-ask spread - Poor liquidity")
        
        return warnings
    
    def _generate_recommendation(self, sentiment, confidence, snapshot) -> str:
        """
        Generate actionable recommendation
        """
        if "EXTREMELY BULLISH" in sentiment:
            move_up = 200 if confidence > 80 else 150
            return f"🚀 STRONGLY BULLISH | Target: {snapshot.ltp + move_up:.0f} (+{move_up:.0f} pts) | SL: {snapshot.ltp - 100:.0f}"
        elif "STRONGLY BULLISH" in sentiment:
            move_up = 150 if confidence > 75 else 100
            return f"😀 BULLISH | Target: {snapshot.ltp + move_up:.0f} (+{move_up:.0f} pts) | SL: {snapshot.ltp - 80:.0f}"
        elif "MODERATELY BULLISH" in sentiment:
            move_up = 100
            return f"😊 MODERATELY BULLISH | Target: {snapshot.ltp + move_up:.0f} (+{move_up:.0f} pts) | SL: {snapshot.ltp - 50:.0f}"
        elif "NEUTRAL" in sentiment:
            return f"😐 NEUTRAL | Wait for direction clarity | Monitor key levels"
        elif "SLIGHTLY BEARISH" in sentiment:
            move_down = 50
            return f"😩 SLIGHTLY BEARISH | Target: {snapshot.ltp - move_down:.0f} (-{move_down:.0f} pts) | SL: {snapshot.ltp + 50:.0f}"
        elif "MODERATELY BEARISH" in sentiment:
            move_down = 100
            return f"😫 MODERATELY BEARISH | Target: {snapshot.ltp - move_down:.0f} (-{move_down:.0f} pts) | SL: {snapshot.ltp + 80:.0f}"
        elif "STRONGLY BEARISH" in sentiment:
            move_down = 150 if confidence > 75 else 100
            return f"😓 STRONGLY BEARISH | Target: {snapshot.ltp - move_down:.0f} (-{move_down:.0f} pts) | SL: {snapshot.ltp + 100:.0f}"
        else:
            move_down = 200 if confidence > 80 else 150
            return f"🙀 EXTREMELY BEARISH | Target: {snapshot.ltp - move_down:.0f} (-{move_down:.0f} pts) | SL: {snapshot.ltp + 150:.0f}"

print("✅ MARKET INTELLIGENCE ANALYZER - READY")
