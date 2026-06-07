"""
📋 COMPLETE MARKET ANALYSIS REPORT
Combines: Live Data + Intelligence Analysis + Gemini AI
"""

import asyncio
import json
from datetime import datetime
from trading_system.live_data.live_market_fetcher import LiveDataPipeline, MarketSnapshot
from trading_system.live_data.market_intelligence_analyzer import MarketIntelligenceAnalyzer, MarketIntelligenceReport
from trading_system.gemini_integration.gemini_api_client import GeminiTradingEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteMarketReport:
    """
    Generate complete market analysis report combining:
    1. Live market data (FII/DII, VIX, OI, PCR, Volume, LTP)
    2. Intelligence analysis (Bullish/Bearish with point targets)
    3. Gemini AI analysis (Advanced multi-timeframe psychology)
    """
    
    def __init__(self, zerodha_key: str, zerodha_token: str, gemini_key: str):
        self.data_pipeline = LiveDataPipeline(zerodha_key, zerodha_token)
        self.analyzer = MarketIntelligenceAnalyzer()
        self.gemini = GeminiTradingEngine(api_key=gemini_key)
    
    async def generate_complete_report(self, symbol: str = "NIFTY50") -> Dict:
        """
        Generate complete market analysis report
        
        Args:
            symbol: Market symbol (e.g., "NIFTY50", "BANKNIFTY")
        
        Returns:
            Complete analysis report with all indicators
        """
        try:
            # Initialize data sources
            await self.data_pipeline.initialize()
            
            logger.info(f"\n{'='*80}")
            logger.info(f"  📋 COMPLETE MARKET ANALYSIS REPORT - {symbol}")
            logger.info(f"{'='*80}\n")
            
            # 1. Fetch complete market snapshot
            logger.info("📊 [STEP 1] Fetching live market data...\n")
            snapshot = await self.data_pipeline.get_complete_market_snapshot(symbol)
            
            # 2. Analyze with intelligence engine
            logger.info("\n📋 [STEP 2] Analyzing market intelligence...\n")
            intelligence_report = self.analyzer.analyze_complete_market(snapshot)
            
            # 3. Analyze with Gemini AI
            logger.info("\n🤖 [STEP 3] Running Gemini AI analysis...\n")
            gemini_input = self._prepare_gemini_input(snapshot)
            gemini_analysis = self.gemini.analyze_market(gemini_input)
            
            # 4. Combine all reports
            complete_report = {
                "report_timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                
                # Market Data
                "market_data": {
                    "ltp": snapshot.ltp,
                    "change": {
                        "points": round(snapshot.change_points, 2),
                        "percent": round(snapshot.change_percent, 2)
                    },
                    "volume": {
                        "current": snapshot.volume,
                        "avg_20": snapshot.volume_avg_20,
                        "ratio": round(snapshot.volume_ratio, 2)
                    }
                },
                
                # Intelligence Analysis
                "intelligence_analysis": {
                    "sentiment": intelligence_report.sentiment,
                    "confidence": round(intelligence_report.confidence, 2),
                    "targets": {
                        "up_points": round(intelligence_report.expected_move_up, 2),
                        "down_points": round(intelligence_report.expected_move_down, 2),
                        "resistance": round(intelligence_report.target_resistance, 2),
                        "support": round(intelligence_report.target_support, 2)
                    },
                    "component_signals": {
                        "fii_signal": round(intelligence_report.fii_signal, 2),
                        "vix_signal": round(intelligence_report.vix_signal, 2),
                        "oi_signal": round(intelligence_report.oi_signal, 2),
                        "pcr_signal": round(intelligence_report.pcr_signal, 2),
                        "volume_signal": round(intelligence_report.volume_signal, 2),
                        "price_signal": round(intelligence_report.price_signal, 2)
                    },
                    "key_factors": intelligence_report.key_factors,
                    "warnings": intelligence_report.warnings,
                    "recommendation": intelligence_report.recommendation
                },
                
                # Gemini AI Analysis
                "gemini_analysis": gemini_analysis,
                
                # Raw Market Indicators
                "market_indicators": {
                    "fii_dii": {
                        "fii_net_flow": round(snapshot.fii_flow.get("net", 0), 2),
                        "fii_equity": round(snapshot.fii_flow.get("equity", 0), 2),
                        "fii_derivatives": round(snapshot.fii_flow.get("derivatives", 0), 2),
                        "dii_net_flow": round(snapshot.dii_flow.get("net", 0), 2),
                        "fii_trend": snapshot.fii_trend
                    },
                    "volatility": {
                        "vix": round(snapshot.vix, 2),
                        "vix_change": round(snapshot.vix_change, 2),
                        "vix_trend": snapshot.vix_trend
                    },
                    "options": {
                        "open_interest": snapshot.open_interest,
                        "oi_change": snapshot.oi_change,
                        "oi_change_percent": round(snapshot.oi_change_percent, 2),
                        "put_call_ratio": round(snapshot.pcr_ratio, 2),
                        "max_pain": snapshot.max_pain,
                        "implied_volatility": round(snapshot.iv, 2)
                    }
                }
            }
            
            # Close connections
            await self.data_pipeline.close()
            
            return complete_report
        
        except Exception as e:
            logger.error(f"\n❌ Error generating report: {e}")
            raise
    
    def _prepare_gemini_input(self, snapshot: MarketSnapshot) -> Dict:
        """
        Prepare market data in Gemini-compatible format
        """
        return {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp.isoformat(),
            "timeframes": {
                "1m": {
                    "current_price": snapshot.ltp,
                    "change_percent": round(snapshot.change_percent, 2),
                    "volume": snapshot.volume,
                    "volume_ratio": round(snapshot.volume_ratio, 2)
                },
                "5m": {
                    "current_price": snapshot.ltp,
                    "change_percent": round(snapshot.change_percent, 2),
                    "volume": snapshot.volume
                },
                "1h": {
                    "current_price": snapshot.ltp,
                    "change_percent": round(snapshot.change_percent, 2),
                    "volume": snapshot.volume
                }
            },
            "derivatives_data": {
                "put_call_ratio": round(snapshot.pcr_ratio, 2),
                "implied_volatility": round(snapshot.iv, 2),
                "open_interest": snapshot.open_interest,
                "max_pain_zone": snapshot.max_pain
            },
            "sentiment_data": {
                "fii_flow_million_usd": round(snapshot.fii_flow.get("net", 0), 2),
                "vix": round(snapshot.vix, 2),
                "market_mood": "bullish" if snapshot.change_percent > 0 else "bearish"
            }
        }
    
    def format_report_for_display(self, report: Dict) -> str:
        """
        Format complete report for console display
        """
        output = f"""
╔{'═'*78}╗
║{'COMPLETE MARKET ANALYSIS REPORT - ' + report['symbol']:<78}║
║{'Timestamp: ' + report['report_timestamp']:<78}║
╚{'═'*78}╝

┌─ CURRENT MARKET STATUS ─────────────────────────────────────────────────────┐
│
│  📊 LTP: {report['market_data']['ltp']:<15} Change: {report['market_data']['change']['points']:+.2f}pts ({report['market_data']['change']['percent']:+.2f}%)
│  📊 Volume: {report['market_data']['volume']['current']:<12} (Avg-20: {report['market_data']['volume']['avg_20']}, Ratio: {report['market_data']['volume']['ratio']:.2f}x)
│
└─────────────────────────────────────────────────────────────────────────────┘

┌─ MARKET INTELLIGENCE ANALYSIS ──────────────────────────────────────────────┐
│
│  🎯 SENTIMENT: {report['intelligence_analysis']['sentiment']:<50}
│  📈 Confidence: {report['intelligence_analysis']['confidence']:.0f}%
│
│  🎯 PRICE TARGETS:
│     ↑ Up: +{report['intelligence_analysis']['targets']['up_points']:.0f} pts → {report['intelligence_analysis']['targets']['resistance']:.0f}
│     ↓ Down: -{report['intelligence_analysis']['targets']['down_points']:.0f} pts → {report['intelligence_analysis']['targets']['support']:.0f}
│
│  🧠 COMPONENT SIGNALS:
│     FII Signal: {report['intelligence_analysis']['component_signals']['fii_signal']:>6.0f} | VIX Signal: {report['intelligence_analysis']['component_signals']['vix_signal']:>6.0f}
│     OI Signal:  {report['intelligence_analysis']['component_signals']['oi_signal']:>6.0f} | PCR Signal: {report['intelligence_analysis']['component_signals']['pcr_signal']:>6.0f}
│     Volume:    {report['intelligence_analysis']['component_signals']['volume_signal']:>6.0f} | Price:    {report['intelligence_analysis']['component_signals']['price_signal']:>6.0f}
│
│  💡 KEY FACTORS:
"""
        
        for factor in report['intelligence_analysis']['key_factors']:
            output += f"│     • {factor}\n"
        
        if report['intelligence_analysis']['warnings']:
            output += "│\n│  ⚠️  WARNINGS:\n"
            for warning in report['intelligence_analysis']['warnings']:
                output += f"│     ⚠️  {warning}\n"
        
        output += f"""
│
│  📌 RECOMMENDATION:
│     {report['intelligence_analysis']['recommendation']}
│
└─────────────────────────────────────────────────────────────────────────────┘

┌─ MARKET INDICATORS (RAW DATA) ───────────────────────────────────────────────┐
│
│  💰 FII/DII FLOWS:
│     FII Net: {report['market_indicators']['fii_dii']['fii_net_flow']:+.2f}M USD | Equity: {report['market_indicators']['fii_dii']['fii_equity']:+.2f}M | Derivatives: {report['market_indicators']['fii_dii']['fii_derivatives']:+.2f}M
│     DII Net: {report['market_indicators']['fii_dii']['dii_net_flow']:+.2f}M USD
│     FII Trend: {report['market_indicators']['fii_dii']['fii_trend'].upper()}
│
│  📊 VOLATILITY (VIX):
│     VIX: {report['market_indicators']['volatility']['vix']:.2f} ({report['market_indicators']['volatility']['vix_change']:+.2f}) | Trend: {report['market_indicators']['volatility']['vix_trend'].upper()}
│
│  🎪 OPTIONS DATA:
│     OI: {report['market_indicators']['options']['open_interest']:,} | OI Change: {report['market_indicators']['options']['oi_change_percent']:+.2f}%
│     PCR: {report['market_indicators']['options']['put_call_ratio']:.2f} | Max Pain: {report['market_indicators']['options']['max_pain']:.0f}
│     IV: {report['market_indicators']['options']['implied_volatility']:.2f}
│
└─────────────────────────────────────────────────────────────────────────────┘

┌─ GEMINI AI ADVANCED ANALYSIS ───────────────────────────────────────────────┐
│
│  🤖 Market State: {report['gemini_analysis'].get('market_state', 'N/A')}
│  📊 AI Confidence: {report['gemini_analysis'].get('signal', {}).get('confidence_percent', 'N/A'):.0f}%
│  🎯 AI Signal: ↑{report['gemini_analysis'].get('signal', {}).get('direction_up_probability', 0):.0f}% | ↓{report['gemini_analysis'].get('signal', {}).get('direction_down_probability', 0):.0f}%
│  ⚠️  Trap Risk: {report['gemini_analysis'].get('signal', {}).get('risk_level', 'N/A')}
│
│  🧠 AI Insights:
"""
        
        for insight in report['gemini_analysis'].get('key_insights', []):
            output += f"│     • {insight}\n"
        
        output += f"""
│
└─────────────────────────────────────────────────────────────────────────────┘

{'═'*80}
"""
        
        return output

# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    
    report_generator = CompleteMarketReport(
        zerodha_key="your_zerodha_api_key",
        zerodha_token="your_zerodha_access_token",
        gemini_key="your_google_api_key"
    )
    
    # Generate complete report
    report = await report_generator.generate_complete_report("NIFTY50")
    
    # Display formatted report
    print(report_generator.format_report_for_display(report))
    
    # Also save as JSON
    with open(f"market_report_{report['symbol']}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n✅ Report saved as market_report_{report['symbol']}.json")

if __name__ == "__main__":
    # Run: python complete_market_report.py
    asyncio.run(main())
