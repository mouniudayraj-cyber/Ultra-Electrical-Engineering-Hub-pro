import google.generativeai as genai
import json
from typing import Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiTradingEngine:
    """
    Integration with Google Gemini AI for market analysis
    Production-ready market intelligence engine
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini API client
        
        Args:
            api_key: Google API key from AI Studio
            model: Model name (default: gemini-2.0-flash for speed)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.api_key = api_key
        
        # Load master prompt
        self.master_prompt = self._load_master_prompt()
        
        logger.info(f"✅ Gemini Trading Engine initialized with {model}")
    
    def _load_master_prompt(self) -> str:
        """
        Load the master trading prompt
        
        Returns:
            Master prompt text
        """
        try:
            with open("trading_system/gemini_integration/master_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Master prompt file not found, using inline prompt")
            return self._get_default_prompt()
    
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send market data to Gemini for analysis
        
        Args:
            market_data: Structured market data dictionary
        
        Returns:
            Parsed JSON response with trading intelligence
        """
        try:
            # Prepare input
            input_json = json.dumps(market_data, indent=2)
            
            # Create prompt
            prompt = f"""{self.master_prompt}

---

## 📊 ANALYZE THIS MARKET DATA:

{input_json}

---

Respond with ONLY the JSON output as specified in the schema.
"""
            
            # Call Gemini API
            logger.info("📡 Sending request to Gemini...")
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON if wrapped in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            analysis_result = json.loads(response_text)
            
            logger.info("✅ Analysis complete")
            return analysis_result
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Response: {response.text}")
            return self._error_response(f"JSON parsing failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            return self._error_response(f"API error: {str(e)}")
    
    def stream_analysis(self, market_data: Dict[str, Any]):
        """
        Stream analysis for real-time updates
        
        Args:
            market_data: Structured market data
        
        Yields:
            Streamed response chunks
        """
        try:
            input_json = json.dumps(market_data, indent=2)
            prompt = f"""{self.master_prompt}

---

Analyze this market data and respond with JSON only:

{input_json}
"""
            
            logger.info("🔴 Streaming analysis...")
            
            with self.model.generate_content(prompt, stream=True) as response:
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            
            logger.info("✅ Streaming complete")
        
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield self._error_response(f"Streaming error: {str(e)}")
    
    def batch_analyze(self, market_data_list: list) -> list:
        """
        Analyze multiple symbols in batch
        
        Args:
            market_data_list: List of market data dictionaries
        
        Returns:
            List of analysis results
        """
        results = []
        
        for i, data in enumerate(market_data_list):
            logger.info(f"Processing {i+1}/{len(market_data_list)}...")
            result = self.analyze_market(data)
            results.append(result)
        
        logger.info(f"✅ Batch analysis complete ({len(results)} symbols)")
        return results
    
    def format_signal_for_display(self, analysis: Dict[str, Any]) -> str:
        """
        Format analysis result for UI/dashboard display
        
        Args:
            analysis: Analysis result from Gemini
        
        Returns:
            Formatted string for display
        """
        try:
            signal = analysis.get("signal", {})
            market_state = analysis.get("market_state", "UNKNOWN")
            insights = analysis.get("key_insights", [])
            warnings = analysis.get("warnings", [])
            
            output = f"""
╔═══════════════════════════════════════════════════════════════╗
║           🤖 GEMINI QUANT ANALYSIS REPORT                   ║
╚═══════════════════════════════════════════════════════════════╝

📊 MARKET STATE: {market_state}

🎯 SIGNAL ANALYSIS:
   ↑ UP Probability:      {signal.get('direction_up_probability', 'N/A'):.0f}%
   ↓ DOWN Probability:    {signal.get('direction_down_probability', 'N/A'):.0f}%
   
   Confidence:            {signal.get('confidence_percent', 'N/A'):.0f}%
   Expected Move:         {signal.get('expected_move_percent', 'N/A')}
   Risk Level:            {signal.get('risk_level', 'N/A')}

💡 KEY INSIGHTS:
"""
            for insight in insights:
                output += f"   • {insight}\n"
            
            if warnings:
                output += "\n⚠️  WARNINGS:\n"
                for warning in warnings:
                    output += f"   ⚠️  {warning}\n"
            
            recommendation = analysis.get("recommendation", "")
            if recommendation:
                output += f"\n📌 RECOMMENDATION:\n   {recommendation}\n"
            
            output += "\n" + "═" * 63 + "\n"
            
            return output
        
        except Exception as e:
            logger.error(f"Formatting error: {e}")
            return f"Error formatting output: {e}"
    
    @staticmethod
    def _error_response(error_msg: str) -> Dict[str, Any]:
        """Generate error response in expected format"""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "symbol": "ERROR",
            "market_state": "ERROR",
            "signal": {
                "direction_up_probability": 0,
                "direction_down_probability": 0,
                "confidence_percent": 0,
                "expected_move_percent": "0 - 0",
                "risk_level": "UNKNOWN"
            },
            "key_insights": [f"Error: {error_msg}"],
            "warnings": ["Analysis failed"],
            "recommendation": "❌ Unable to generate signal. Please check data and try again."
        }
    
    @staticmethod
    def _get_default_prompt() -> str:
        """Get default prompt if file not found"""
        return """
You are a Quant Trading Intelligence Engine. Analyze market data and output JSON only.
Respond with structured analysis of fear, greed, trap probability, and institutional flow across timeframes.
"""

# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize
    engine = GeminiTradingEngine(api_key="YOUR_GOOGLE_API_KEY")
    
    # Sample market data
    sample_data = {
        "symbol": "NIFTY50",
        "exchange": "NSE",
        "timestamp": "2024-01-15T14:30:00Z",
        "timeframes": {
            "5m": {
                "current_price": 50030,
                "atr_14": 120,
                "rsi_14": 65,
                "sma_20": 49900
            },
            "15m": {
                "current_price": 50030,
                "atr_14": 150,
                "rsi_14": 58,
                "sma_20": 49850
            },
            "1h": {
                "current_price": 50030,
                "atr_14": 200,
                "rsi_14": 55,
                "sma_20": 49800
            }
        },
        "derivatives_data": {
            "put_call_ratio": 1.15,
            "implied_volatility": 18.5,
            "max_pain_zone": 50000
        }
    }
    
    # Analyze
    result = engine.analyze_market(sample_data)
    
    # Display
    print(engine.format_signal_for_display(result))
